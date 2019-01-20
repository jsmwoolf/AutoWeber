from AutoWeber import AutoWeber

weber = AutoWeber()
weber.loadHtml("./examples/basic/testBasic.html")
weber.addData("Test1")
weber.addData("Test2")
weber.writeStructureToJson("basic-struct.json")