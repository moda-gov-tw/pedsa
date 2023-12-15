export let comparedata = {
    "status": 0,
    "dataInfo": {
        "importlist": [
            {
                "dataset": "Mock_W1_smoking_userdata.csv",
                "dataset_count": 123,
                "col_setting": [
                    {
                        "col": "name",
                        "func": "no"
                    },
                    {
                        "col": "ID",
                        "func": "Aes"
                    },
                    {
                        "col": "SID",
                        "func": "Hash"
                    }
                ],
            },
            {
                "dataset": "Mock_W2_smoking_data.csv",
                "dataset_count": 456,
                "col_setting": [
                    {
                        "col": "ID",
                        "func": "Hash"
                    },
                    {
                        "col": "SBP",
                        "func": "no"
                    },
                    {
                        "col": "BLDS",
                        "func": "no"
                    }
                ],
            },
            {
                "dataset": "Mock_W3_smoking_detail.csv",
                "dataset_count": 789,
                "col_setting": [
                    {
                        "col": "ID",
                        "func": "Hash"
                    },
                    {
                        "col": "urine_protein",
                        "func": "no"
                    },
                    {
                        "col": "SGOT",
                        "func": "no"
                    }
                ],
            },
        ],
    },
    "datacompare": [
        {
            "dataset": "w1_a.csv*w2_b.csv",
            "match": "N",
            "col": "ID_ID",
            "colmatch": "Y"
        },
        {
            "dataset": "w1_a.csv*w3_c.csv",
            "match": "N",
            "col": "ID_ID",
            "colmatch": "Y"
        }
    ]

}
