import * as os from 'os'
import {exec, getExecOutput} from '../src/exec.js'

describe('real child-process line output', () => {
  const values = [
    '',
    'tail',
    `first${os.EOL}tail`,
    `${os.EOL}${os.EOL}`,
    `α🙂א${os.EOL}終`,
    `α🙂א${os.EOL}終${os.EOL}`,
    'x'.repeat(128 * 1024) + '終',
    Buffer.from([0x61, 0xe2, 0x82])
  ]
  it.each(values.map((value, i) => [i, Buffer.from(value)] as const))(
    'delivers exact lines and raw output for payload %s',
    async (_i, bytes) => {
      const lines: string[] = []
      const errors: string[] = []
      const raw: Buffer[] = []
      const result = await getExecOutput(
        `"${process.execPath}"`,
        [
          '-e',
          "const a=[];process.stdin.on('data',b=>a.push(b));process.stdin.on('end',()=>{const b=Buffer.concat(a);process.stdout.write(b);process.stderr.write(b)})"
        ],
        {
          silent: true,
          input: bytes,
          listeners: {
            stdline: line => lines.push(line),
            errline: line => errors.push(line),
            stdout: data => raw.push(data)
          }
        }
      )
      const expected = bytes.length ? bytes.toString('utf8').split(os.EOL) : []
      if (expected[expected.length - 1] === '') expected.pop()
      expect(result.exitCode).toBe(0)
      expect(lines).toEqual(expected)
      expect(errors).toEqual(expected)
      expect(Buffer.concat(raw)).toEqual(bytes)
      expect(result.stdout).toBe(bytes.toString('utf8'))
      expect(result.stderr).toBe(bytes.toString('utf8'))
    }
  )

  it.each([false, true])(
    'flushes on native nonzero exit, ignoreReturnCode=%s',
    async ignoreReturnCode => {
      const lines: string[] = []
      const pending = exec(
        `"${process.execPath}"`,
        ['-e', "process.stdout.write('last diagnostic');process.exitCode=7"],
        {
          silent: true,
          ignoreReturnCode,
          listeners: {stdline: line => lines.push(line)}
        }
      )
      if (ignoreReturnCode) await expect(pending).resolves.toBe(7)
      else await expect(pending).rejects.toThrow('exit code 7')
      expect(lines).toEqual(['last diagnostic'])
    }
  )

  it('flushes stderr before a failOnStdErr rejection', async () => {
    const lines: string[] = []
    const pending = exec(
      `"${process.execPath}"`,
      ['-e', "process.stderr.write('diagnostic')"],
      {
        silent: true,
        failOnStdErr: true,
        listeners: {errline: line => lines.push(line)}
      }
    )
    await expect(pending).rejects.toThrow('STDERR stream')
    expect(lines).toEqual(['diagnostic'])
  })
})
