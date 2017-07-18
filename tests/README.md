To test (currently):

```bash
npm install
npm run selenium
jupyter notebook --config=./jupyter_notebook_config.json --port=5678 --no-browser
node node_modules/nightwatch/bin/nightwatch --config nightwatch.js --env local_chromee
```
