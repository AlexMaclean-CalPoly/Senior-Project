const { spawn } = require('node:child_process');
const ls = spawn('python', ['ch.py']);

ls.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

ls.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

ls.stdin.write("hello\n")

for (let index = 0; index < 10000; index++) {
    const element = 10000;

}
ls.stdin.write("hello2\n")

ls.on('close', (code) => {
  console.log(`child process exited with code ${code}`);
});