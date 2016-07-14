### Submitting a new release to PyPI:

Commit changes in git. Then:

```shell
python setup.py sdist upload
git tag -a X.X.X -m 'comment'
git push
git push --tags
```

### Submitting a new release to NPM:
```shell
cd js
git clean -fdx # nuke the  `dist` and `node_modules`
npm install
npm publish
```