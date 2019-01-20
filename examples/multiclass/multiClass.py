from AutoWeber import AutoWeber

weber = AutoWeber()
weber.loadHtml("./test/basic/testGroupingMultiClass.html")
weber.addData("Test1")
weber.addData("Test2")
weber.writeStructureToJson("multiClass-struct.json")