from AutoWeber import AutoWeber
weber = AutoWeber()
weber.loadHtml("https://www.kaggle.com/datasets")
weber.addData("FIFA 19 complete player dataset")
weber.addData("U.S. Education Datasets: Unification Project")
weber.writeStructureToJson('kaggle-dataset-struct')