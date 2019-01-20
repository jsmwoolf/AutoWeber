from AutoWeber import AutoWeber
weber = AutoWeber()
weber.loadHtml("https://issuehunt.io/repos")
weber.addData("EconoMe")
weber.addData("Javascript")
weber.addData("Available funds")
weber.addData("gtw")
weber.addData("clapme")
weber.addData("gconfigs")
weber.writeStructureToJson('issueHunt-repo-struct')