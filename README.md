## add_migap.sh
usegalaxyコンテナにMiGAPツールを追加する処理を実行するためのシェルスクリプト。Galaxy起動後に実行し、実行後usegalaxyコンテナを再起動する。

### Usage
```usage
sh add_migap.sh <usegalaxyコンテナのcontainer id>
docker restart <usegalaxyコンテナのcontainer id>
```

## add_migap_megap.sh
usegalaxyコンテナにMiGAPツールとMeGAP (preanalysis)ツールを追加する処理を実行するためのシェルスクリプト。Galaxy起動後に実行し、実行後usegalaxyコンテナを再起動する。

### Usage
```usage
sh add_migap_megap.sh <usegalaxyコンテナのcontainer id>
docker restart <usegalaxyコンテナのcontainer id>
```

## MiGAP_workflow.json
GalaxyにMiGAPワークフローを登録するには、GalaxyのWorkflowメニューからこのファイルをimportする。

## MeGAP_workflow.json
GAlaxyにMeGAP (preanalysis)ワークフローを登録するには、GalaxyのWorkflowメニューからこのファイルをimportする。
