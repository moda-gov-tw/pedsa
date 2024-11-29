export let projectInsertPayload = {
    "project_name": "前端測試(藥品安全)",
    "project_eng": "frontend_drugs",
    "project_desc": "frontend_drugs",
    "enc_key": "XXXAAABBBCCCC",
    "group_id": 1,
    "aes_col": "age_w2_b,sex_w1_a,age_w1_a",
    "jointablecount": 367,
    "jointablename": "PP_smoking_drinking_enc",
    "join_type": 0,
    "join_func": [
        {
            "left_datasetname": "w3_a.csv",
            "left_col": "ID",
            "right_datasetname": "w4_c.csv",
            "right_col": "ID"
        },
        {
            "left_datasetname": "w3_a.csv",
            "left_col": "ID",
            "right_datasetname": "w5_b.csv",
            "right_col": "ID"
        }
    ],
    "project_role": [
        {
            "member_id": 8,
            "group_id": 6,
            "member_role": 5
        },
        {
            "member_id": 6,
            "group_id": 4,
            "member_role": 4
        },
        {
            "member_id": 11,
            "group_id": 5,
            "member_role": 5
        },
        {
            "member_id": 13,
            "group_id": 4,
            "member_role": 3
        }
    ]
}