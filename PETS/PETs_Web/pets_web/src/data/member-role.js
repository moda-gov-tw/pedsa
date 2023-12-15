export let member_roles = [
    '專案使用者', '專案資料提供者'
];
// '專案管理者',
export let system_roles = [
    '單位管理員', '專案管理員',
];

export let system_roles_dic = {
    '單位管理員': 'group_admin',
    '專案管理員': 'project_admin',
};

export let member_roles_id_dic = {
    '專案管理者': 3,
    '專案使用者': 4,
    '專案資料提供者': 5
};

export let roles_id_member_dic = {
    3: '專案管理者',
    4: '專案使用者',
    5: '專案資料提供者'
};