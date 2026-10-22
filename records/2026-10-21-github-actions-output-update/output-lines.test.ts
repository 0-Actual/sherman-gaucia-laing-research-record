import {EventEmitter} from 'events'
import * as child from 'child_process'
import * as os from 'os'
import {exec, getExecOutput} from '../src/exec.js'
import {ToolRunner} from '../src/toolrunner.js'
import {ExecOptions} from '../src/interfaces.js'

jest.mock('child_process', () => ({spawn: jest.fn()}))
jest.mock('@actions/io', () => ({
  which: jest.fn(async () => process.execPath)
}))
jest.mock('@actions/io/lib/io-util', () => ({
  isRooted: () => true,
  exists: async () => true
}))

function expectedLines(bytes: Buffer): string[] {
  if (bytes.length === 0) return []
  const result = bytes.toString('utf8').split(/\r?\n/)
  if (result[result.length - 1] === '') result.pop()
  return result
}

function fakeChild(): EventEmitter & {
  stdout: EventEmitter
  stderr: EventEmitter
} {
  return Object.assign(new EventEmitter(), {
    stdout: new EventEmitter(),
    stderr: new EventEmitter()
  })
}

const texts: Array<[string, Buffer]> = [
  ['empty', Buffer.alloc(0)],
  ['ASCII tail', Buffer.from('final record')],
  ['terminated', Buffer.from(`first${os.EOL}second${os.EOL}`)],
  ['blank lines', Buffer.from(`${os.EOL}${os.EOL}tail`)],
  ['Unicode tail', Buffer.from(`α🙂א${os.EOL}終`)],
  ['Unicode terminated', Buffer.from(`α🙂א${os.EOL}終${os.EOL}`)],
  ['incomplete UTF8', Buffer.from([0x61, 0xe2, 0x82])],
  ['invalid UTF8', Buffer.from([0xff, 0xe2, 0x28, 0xa1])],
  ['non-native newline', Buffer.from(`a${os.EOL === '\r\n' ? '\n' : '\r\n'}b`)],
  ['mixed LF and CRLF', Buffer.from('a\nb\r\nc\n終')],
  ['lone CR and final CR', Buffer.from('a\rb\r')],
  ['CR immediately before CRLF', Buffer.from('a\r\r\nb')]
]

describe('line output is independent of transport chunks', () => {
  afterEach(() => jest.clearAllMocks())

  for (const [name, bytes] of texts) {
    for (let cut = 0; cut <= bytes.length; cut++) {
      it(`${name}, split at byte ${cut}`, async () => {
        const cp = fakeChild()
        jest.mocked(child.spawn).mockReturnValue(cp as child.ChildProcess)
        const stdout: string[] = []
        const stderr: string[] = []
        const rawOut: Buffer[] = []
        const rawErr: Buffer[] = []
        const pending = getExecOutput('synthetic-tool', [], {
          silent: true,
          listeners: {
            stdline: line => stdout.push(line),
            errline: line => stderr.push(line),
            stdout: data => rawOut.push(data),
            stderr: data => rawErr.push(data)
          }
        })
        await new Promise<void>(resolve => setImmediate(resolve))
        const chunks = [bytes.subarray(0, cut), bytes.subarray(cut)]
        for (const chunk of chunks) {
          cp.stdout.emit('data', chunk)
          cp.stderr.emit('data', chunk)
        }
        cp.emit('exit', 0)
        cp.emit('close', 0)
        const result = await pending
        expect(result.exitCode).toBe(0)
        expect(stdout).toEqual(expectedLines(bytes))
        expect(stderr).toEqual(expectedLines(bytes))
        expect(result.stdout).toBe(bytes.toString('utf8'))
        expect(result.stderr).toBe(bytes.toString('utf8'))
        expect(Buffer.concat(rawOut)).toEqual(bytes)
        expect(Buffer.concat(rawErr)).toEqual(bytes)
      })
    }
  }

  it('keeps stdout and stderr decoders independent across bytewise interleaving', async () => {
    const cp = fakeChild()
    jest.mocked(child.spawn).mockReturnValue(cp as child.ChildProcess)
    const out = Buffer.from(`🙂${os.EOL}α`)
    const err = Buffer.from(`終${os.EOL}א`)
    const stdout: string[] = []
    const stderr: string[] = []
    const pending = exec('synthetic-tool', [], {
      silent: true,
      listeners: {
        stdline: line => stdout.push(line),
        errline: line => stderr.push(line)
      }
    })
    await new Promise<void>(resolve => setImmediate(resolve))
    for (let i = 0; i < Math.max(out.length, err.length); i++) {
      if (i < out.length) cp.stdout.emit('data', out.subarray(i, i + 1))
      if (i < err.length) cp.stderr.emit('data', err.subarray(i, i + 1))
    }
    cp.emit('exit', 0)
    cp.emit('close', 0)
    await pending
    expect(stdout).toEqual(expectedLines(out))
    expect(stderr).toEqual(expectedLines(err))
  })

  it.each([
    ['nonzero', 7, {}, true],
    ['ignored nonzero', 7, {ignoreReturnCode: true}, false],
    ['stderr failure', 0, {failOnStdErr: true}, true]
  ] as Array<[string, number, ExecOptions, boolean]>)(
    'flushes tails before settling %s',
    async (_name, code, options, rejects) => {
      const cp = fakeChild()
      jest.mocked(child.spawn).mockReturnValue(cp as child.ChildProcess)
      const stdout: string[] = []
      const stderr: string[] = []
      const pending = exec('synthetic-tool', [], {
        ...options,
        silent: true,
        listeners: {
          stdline: line => stdout.push(line),
          errline: line => stderr.push(line)
        }
      }).then(
        value => ({value, error: false}),
        () => ({value: undefined, error: true})
      )
      await new Promise<void>(resolve => setImmediate(resolve))
      cp.stdout.emit('data', Buffer.from('out tail'))
      cp.stderr.emit('data', Buffer.from('err tail'))
      cp.emit('exit', code)
      cp.emit('close', code)
      expect((await pending).error).toBe(rejects)
      expect(stdout).toEqual(['out tail'])
      expect(stderr).toEqual(['err tail'])
    }
  )

  it('flushes once when exit is followed by delayed stream closure', async () => {
    jest.useFakeTimers()
    try {
      const cp = fakeChild()
      jest.mocked(child.spawn).mockReturnValue(cp as child.ChildProcess)
      const lines: string[] = []
      const pending = exec('synthetic-tool', [], {
        silent: true,
        delay: 10,
        listeners: {stdline: line => lines.push(line)}
      })
      await Promise.resolve()
      cp.stdout.emit('data', Buffer.from('tail'))
      cp.emit('exit', 0)
      jest.advanceTimersByTime(10)
      await pending
      cp.emit('close', 0)
      expect(lines).toEqual(['tail'])
    } finally {
      jest.useRealTimers()
    }
  })

  it('retains the existing ToolRunner tail event for direct consumers', async () => {
    const cp = fakeChild()
    jest.mocked(child.spawn).mockReturnValue(cp as child.ChildProcess)
    const runner = new ToolRunner('synthetic-tool', [], {silent: true})
    const lines: string[] = []
    runner.on('stdline', line => lines.push(line))
    const pending = runner.exec()
    await new Promise<void>(resolve => setImmediate(resolve))
    cp.stdout.emit('data', Buffer.from('tail'))
    cp.emit('exit', 0)
    cp.emit('close', 0)
    await pending
    expect(lines).toEqual(['tail'])
  })

  it('treats a throwing tail listener as best effort, like complete lines', async () => {
    const cp = fakeChild()
    jest.mocked(child.spawn).mockReturnValue(cp as child.ChildProcess)
    const debug = jest.fn()
    const listener = jest.fn(() => {
      throw new Error('listener failed')
    })
    const pending = exec('synthetic-tool', [], {
      silent: true,
      listeners: {stdline: listener, debug}
    })
    await new Promise<void>(resolve => setImmediate(resolve))
    cp.stdout.emit('data', Buffer.from('tail'))
    cp.emit('exit', 0)
    cp.emit('close', 0)
    await expect(pending).resolves.toBe(0)
    expect(listener).toHaveBeenCalledWith('tail')
    expect(debug).toHaveBeenCalledWith(
      expect.stringContaining('listener failed')
    )
  })
})
