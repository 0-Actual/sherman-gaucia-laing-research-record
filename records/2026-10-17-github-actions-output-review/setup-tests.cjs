const fs = require('node:fs')
const path = require('node:path')
const root = __dirname
const tools = path.join(root, 'tools/node_modules')
for (const edition of ['upstream', 'candidate']) {
  const target = path.join(root, edition)
  const config = {
    rootDir: target,
    testEnvironment: 'node',
    testMatch: ['**/__tests__/*.test.ts'],
    moduleNameMapper: {
      '^(\\.{1,2}/.*)\\.js$': '$1',
      '^@actions/io$': '<rootDir>/packages/io/src/io.ts',
      '^@actions/io/lib/io-util$': '<rootDir>/packages/io/src/io-util.ts'
    },
    transform: {
      '^.+\\.ts$': [path.join(tools, 'ts-jest'), {
        diagnostics: true,
        tsconfig: {
          target: 'ES2020', module: 'commonjs', moduleResolution: 'node',
          esModuleInterop: true, strict: true,
          typeRoots: [path.join(tools, '@types')],
          baseUrl: target,
          paths: {
            '@actions/io': ['packages/io/src/io.ts'],
            '@actions/io/lib/io-util': ['packages/io/src/io-util.ts']
          }
        }
      }]
    },
    testTimeout: 70000,
    maxWorkers: 1,
    cacheDirectory: path.join(root, 'test-cache', edition)
  }
  fs.writeFileSync(path.join(target, 'review-jest.config.cjs'), 'module.exports = ' + JSON.stringify(config, null, 2) + '\n')
}
