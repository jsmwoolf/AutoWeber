from AutoWeber import AutoWeber
weber = AutoWeber()
weber.loadHtml("https://projecteuler.net/archives")
weber.addData("Largest palindrome product")
weber.addData("Goldbach's other conjecture")
weber.addData("Coin sums")
weber.addData("Pentagon numbers")
weber.addData("34")
weber.addData("14")
weber.writeStructureToJson('projecteuler-struct')