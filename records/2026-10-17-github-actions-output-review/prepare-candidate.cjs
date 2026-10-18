const fs = require('node:fs')
const path = require('node:path')
const root = __dirname
let source = fs.readFileSync(path.join(root, 'upstream/packages/exec/src/toolrunner.ts'), 'utf8')
function replace(oldText, newText) {
  if (source.split(oldText).length !== 2) throw Error('Expected one replacement: ' + oldText)
  source = source.replace(oldText, newText)
}
replace("import * as stream from 'stream'", "import * as stream from 'stream'\nimport {StringDecoder} from 'string_decoder'")
replace('    data: Buffer,\n    strBuffer: string,\n    onLine: (line: string) => void\n', '    data: string,\n    strBuffer: string,\n    onLine: (line: string) => void,\n    flush = false\n')
replace('      let s = strBuffer + data.toString()', '      let s = strBuffer + data')
replace('      return s\n    } catch (err)', '      if (flush && s.length > 0) {\n        onLine(s)\n        return \'\'\n      }\n\n      return s\n    } catch (err)')
replace("      let stdbuffer = ''", `      const stdoutDecoder = new StringDecoder('utf8')
      const stderrDecoder = new StringDecoder('utf8')
      const onStdline = (line: string): void => {
        if (this.options.listeners && this.options.listeners.stdline) {
          this.options.listeners.stdline(line)
        }
      }
      const onErrline = (line: string): void => {
        if (this.options.listeners && this.options.listeners.errline) {
          this.options.listeners.errline(line)
        }
      }

      let stdbuffer = ''`)
replace(`            data,
            stdbuffer,
            (line: string) => {
              if (this.options.listeners && this.options.listeners.stdline) {
                this.options.listeners.stdline(line)
              }
            }`, `            stdoutDecoder.write(data),
            stdbuffer,
            onStdline`)
replace(`            data,
            errbuffer,
            (line: string) => {
              if (this.options.listeners && this.options.listeners.errline) {
                this.options.listeners.errline(line)
              }
            }`, `            stderrDecoder.write(data),
            errbuffer,
            onErrline`)
replace(`      state.on('done', (error: Error, exitCode: number) => {
        if (stdbuffer.length > 0) {
          this.emit('stdline', stdbuffer)
        }

        if (errbuffer.length > 0) {
          this.emit('errline', errbuffer)
        }`, `      state.on('done', (error: Error, exitCode: number) => {
        stdbuffer += stdoutDecoder.end()
        errbuffer += stderrDecoder.end()
        if (stdbuffer.length > 0) {
          this._processLineBuffer('', stdbuffer, onStdline, true)
          this.emit('stdline', stdbuffer)
        }

        if (errbuffer.length > 0) {
          this._processLineBuffer('', errbuffer, onErrline, true)
          this.emit('errline', errbuffer)
        }`)
fs.writeFileSync(path.join(root, 'candidate/packages/exec/src/toolrunner.ts'), source)
for (const edition of ['upstream', 'candidate']) {
  for (const name of ['output-lines.test.ts', 'output-lines-integration.test.ts']) {
    fs.copyFileSync(path.join(root, name), path.join(root, edition, 'packages/exec/__tests__', name))
  }
}
