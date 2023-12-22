import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
    Box,
    Button,
    Divider,
    Grid,
    IconButton,
    InputLabel,
    Select,
    Stack,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableRow,
    MenuItem,
    TextField,
    Typography,
    Tooltip,
    useMediaQuery, DialogTitle, Dialog,
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';

// third-party
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import Layout from 'layout';
import ColumnConnect from 'sections/apps/data-connect/column-connect';
import { member_roles, member_roles_id_dic } from '../../../data/member-role';
import BasicAutocomplete from '../../../sections/components-overview/autocomplete/BasicAutocomplete';
import Page from 'components/Page';
import ScrollX from 'components/ScrollX';
import MainCard from 'components/MainCard';
import { projectUpdatePayload } from '../../../utils/mock-project-update-example';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import {
    HeaderSort,
    IndeterminateCheckbox,
    TableRowSelection
} from 'components/third-party/ReactTable';
import ProjectStepper from 'sections/apps/progress/project_stepper';
import { roles_id_member_dic } from 'data/member-role';
import { join_method_dic, id_to_join_method_dic } from 'data/join-method';
import petsLog from 'sections/apps/logger/insert-system-log';
// mock data
import { mockMembers } from "../../../utils/mock-members";
import { mockProjectMembers } from '../../../utils/mock-project-members';
import ConnectSetting from "../../../sections/apps/data-connect/connect-setting";
import useUser from "../../../hooks/useUser";
import { ConfigContext } from "../../../contexts/ConfigContext";
import getALLGroups from "utils/getGroups";
import getALLUsers from "utils/getUsers";
import RemoveCircleOutlineIcon from "@mui/icons-material/RemoveCircleOutline";
import AddIcon from "@mui/icons-material/Add";
//import { projectDetail } from '../../../utils/mock-project-detail';

function ReactTable({ columns, data }) {
    const theme = useTheme();
    const router = useRouter();
    const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
    const filterTypes = useMemo(() => renderFilterTypes, []);
    const sortBy = { id: 'fatherName', desc: false };

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        prepareRow,
        rows,
        state: { globalFilter, selectedRowIds },
        preGlobalFilteredRows,
        setGlobalFilter,
    } = useTable(
        {
            columns,
            data,
            filterTypes,
            initialState: {
                pageIndex: 0, pageSize: 10, sortBy: [sortBy],
                hiddenColumns: []
            }
        },
        useGlobalFilter,
        useFilters,
        useSortBy,
        useExpanded,
        usePagination,
        useRowSelect
    );

    return (
        <>
            <TableRowSelection selected={Object.keys(selectedRowIds).length} />
            <Stack spacing={3}>
                <Table {...getTableProps()}>
                    <TableHead>
                        {headerGroups.map((headerGroup, index) => (
                            <TableRow {...headerGroup.getHeaderGroupProps()} key={index} sx={{ '& > th:first-of-type': { width: '58px' } }}>
                                {headerGroup.headers.map((column, i) => (
                                    <TableCell {...column.getHeaderProps([{ className: column.className }])} key={i}>
                                        <HeaderSort column={column} sort />
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableHead>
                    <TableBody {...getTableBodyProps()}>
                        {rows.map((row, i) => {
                            prepareRow(row);
                            return (
                                <TableRow key={i} {...row.getRowProps()}>
                                    {row.cells.map((cell, index) => (
                                        <TableCell key={index} {...cell.getCellProps([{ className: cell.column.className }])}>
                                            {cell.render('Cell')}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </Stack>
        </>
    );
}

ReactTable.propTypes = {
    columns: PropTypes.array,
    data: PropTypes.array,
    getHeaderProps: PropTypes.func,
    handleAdd: PropTypes.func,
};

const ActionsCell = (row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles) => {
    // console.log('row in ActionsCell', row);

    const handleClick = () => {
        console.log('remove member');
    }
    async function handleRemoveMember() {
        let index1 = projectMembers.findIndex(function (temp) {
            return temp.member_id === row.original.member_id;
        });
        const newProjectMembers = [
            ...projectMembers.slice(0, index1),
            ...projectMembers.slice(index1 + 1)
        ];
        let index2 = projectRoles.findIndex(function (temp) {
            return temp.member_id === row.original.member_id;
        });
        const newProjectRoles = [
            ...projectRoles.slice(0, index2),
            ...projectRoles.slice(index2 + 1)
        ];

        await setProjectMembers(newProjectMembers);
        await setProjectRoles(newProjectRoles);
    }

    return (
        <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
            <Tooltip title="more">
                <IconButton onClick={handleRemoveMember}>
                    <ClearIcon />
                </IconButton>
            </Tooltip>
        </Stack>
    );
};

ActionsCell.propTypes = {
    row: PropTypes.object,
    setTaskData: PropTypes.func,
    setOpenConditions: PropTypes.func,
    theme: PropTypes.array
};

// Main Page
const EditProject = () => {
    const theme = useTheme();
    const router = useRouter();
    const user = useUser();
    const { data: session } = useSession();
    const { allUsers, setAllUsers, allGroups, setAllGroups, userPermission } = useContext(ConfigContext); // 所有單位、人員

    const [project_id, setProject_id] = useState(null);
    const [dataJoinMethod, setDataJoinMethod] = useState('Inner join');
    const [isDataProvider, setIsDataProvider] = useState(false);

    const [enckey, setEnckey] = useState(''); //金鑰
    const [firstDownload, setFirstDownload] = useState(true);
    const [keyDownload, setKeydownload] = useState(false);

    const [selectedGroup, setSelectedGroup] = useState('機關A'); //選擇專案成員單位
    const [memberOptions, setMemberOptions] = useState([]);  //機關下成員選項
    const [selectedMember, setSelectedMember] = useState(null);
    const [selectedMemberId, setSelectedMemberId] = useState(null);
    const [selectedUserRole, setSelectedUserRole] = useState('專案使用者');  //選擇專案成員角色

    const [projectMembers, setProjectMembers] = useState([]);  //專案成員表格資料
    const [projectRoles, setProjectRoles] = useState([]); // member_role

    const [responseProjectStatus, setResponseProjectStatus] = useState([]); // 專案狀態 (進度條)

    const [dataConnectSettings, setDataConnectSettings] = useState([{ left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' }]);
    const [columnSettingCount, setColumnSettingCount] = useState(2);
    const [columnSettingContent, setColumnSettingContent] = useState(<></>);
    const [projectDetail, setProjectDetail] = useState([]);
    const [checkPopUp, setCheckPopUp] = useState(false);
    const [popUpMsg, setPopUpMsg] = useState(null);
    const [userSelectAutocomplete, setUserSelectAutocomplete] = useState(<BasicAutocomplete options={memberOptions} inputValue={selectedMember} setInputValue={setSelectedMember} setSelectedId={setSelectedMemberId} fullWidth />)
    const [canEditProject, setCanEditProject] = useState(true);

    const [updateStatue, setUpdateStatue] = useState(false);
    const [wroteLog, setWroteLog] = useState({});

    const getUserInfo = async (token) => {
        console.log('getUserInfo');
        await axios.get(`/api/user/get_info/${user.id}`, {
            headers: {
                Authorization: `Bearer ${token}`
            }
        })
            .then(async (response) => {
                console.log('get user info', response.data.obj);
                let userRolesInfo = await response.data.obj.role;
                if (Object.keys(userRolesInfo['project_data_provider']).length !== 0) {
                    console.log('userRolesInfo', userRolesInfo['project_data_provider']);
                    await setIsDataProvider(true);
                }
            })
            .catch((error) => {
                console.log('get user info error', error);
            });
    }

    useEffect(() => {
        // Get project_id
        setProject_id(router.query.project_id);
        // Get user role
        // getUserInfo(session.tocken.loginUserToken);
        // console.log('project_group_id', router.query.project_group_id);
        getALLGroups(setAllGroups, session.tocken.loginUserToken); // get all groups
        getALLUsers(setAllUsers, session.tocken.loginUserToken); // get all users
    }, []);
    // console.log("Get the project_id:", project_id);

    useEffect(() => {
        if (project_id) {
            // Fetch API /projects/detail
            const payload = {
                project_id: project_id,
            };
            const config = {
                headers: {
                    Authorization: `Bearer ${session.tocken.loginUserToken}`
                },
            };
            axiosPlus({
                method: "POST",
                stateArray: [projectDetail, setProjectDetail],
                url: "/api/project/post_projectDetail",
                payload: payload,
                config: config,
                showSuccessMsg: false,
            });

            // Update project stauts
            const payloadUpdateStatus = {
                project_id: project_id,
                status: 1,
            };
            const configUpdateStatus = {
                headers: {
                    Authorization: `Bearer ${session.tocken.loginUserToken}`
                },
            };
            const promiseUpdateStatus = axiosPlus({
                method: "PUT",
                stateArray: null,
                url: "/api/project/put_projectStatus",
                payload: payloadUpdateStatus,
                config: configUpdateStatus,
                showSuccessMsg: false,
            });
            promiseUpdateStatus.then((response) => {
                // console.log("promiseUpdateStatus", response);
                if (response && response.data.status == true)
                    setUpdateStatue(true);
            })
        }
    }, [project_id])

    // API /projects/status
    useEffect(() => {
        if (project_id) {
            const config = {
                headers: {
                    Authorization: `Bearer ${session.tocken.loginUserToken}`,
                },
                params: {
                    project_id: project_id,
                },
            };
            axiosPlus({
                method: "GET",
                stateArray: [responseProjectStatus, setResponseProjectStatus],
                url: "/api/project/get_projectStatus",
                config: config,
                showSuccessMsg: false,
            });
        }
    }, [updateStatue]);
    const projectStatus = Number(responseProjectStatus.status);

    // Process the format of api json
    function preprocessAPI(state) {
        // console.log('projectDetail', projectDetail);
        var newJoinFunc_array = [];

        if (state["join_func"]) {
            const joinfunc_array = state["join_func"];
            for (let i = 0; i < (joinfunc_array.length); i++) {
                newJoinFunc_array.push({ "link_col": [joinfunc_array[i].left_datasetname, joinfunc_array[i].left_col, joinfunc_array[i].right_datasetname, joinfunc_array[i].right_col] });
            }
            state.Join_func = newJoinFunc_array;
        }
        return state;
    }

    function getOriDataConnectSettings(projectDetail) {
        let oriDataConnectSettings = [];
        if (projectDetail["join_func"]) {
            let joinfunc_array = projectDetail["join_func"];
            for (let i = 0; i < (joinfunc_array.length); i++) {
                oriDataConnectSettings.push({
                    "left_datasetname": joinfunc_array[i].left_datasetname,
                    "left_col": joinfunc_array[i].left_col,
                    "right_datasetname": joinfunc_array[i].right_datasetname,
                    "right_col": joinfunc_array[i].right_col
                })
            }
            console.log('oriDataConnectSettings', oriDataConnectSettings);
            setColumnSettingCount(joinfunc_array.length);
            setDataConnectSettings(oriDataConnectSettings);
        }
    }

    // get project members
    async function getProjectMembers(projectDetail) {
        console.log('get project members', projectDetail["project_role"]);
        let projectMembersList = [];
        let projectMemberRolesList = [];
        if (projectDetail["project_role"]) {
            await Promise.all(
                await projectDetail.project_role.map(async (pmr) => {
                    await axios.get(`/api/user/get_info/${pmr.member_id}`, {
                        headers: {
                            Authorization: `Bearer ${session.tocken.loginUserToken}`
                        }
                    })
                        .then(async (res) => {
                            console.log('get project members', res);
                            let temp = {};
                            temp['member_id'] = pmr.member_id;
                            temp['member_role'] = pmr.project_role;
                            temp['user_role'] = roles_id_member_dic[pmr.project_role]
                            temp['group_id'] = res.data.obj.group_id;
                            temp['group_name'] = res.data.obj.group_name;
                            temp['user_name'] = res.data.obj.username;
                            temp['user_email'] = res.data.obj.email;
                            console.log('temp', temp);
                            projectMembersList.push(temp);
                            projectMemberRolesList.push({
                                'member_id': pmr.member_id,
                                'group_id': res.data.obj.group_id,
                                'member_role': pmr.project_role
                            })
                        })
                        .catch((error) => {
                            console.log('get project members', error);
                        })
                })
            )
            console.log('projectMembersList', projectMembersList);
            setProjectMembers(projectMembersList);
            setProjectRoles(projectMemberRolesList);
        }
    }

    useEffect(() => {
        setDataJoinMethod(id_to_join_method_dic[Number(projectDetail.join_type)])
        getOriDataConnectSettings(projectDetail);
        getProjectMembers(projectDetail);
        if (projectDetail) {
            if (projectDetail.project_name) {
                // console.log("projectDetail", projectDetail);
                if (!wroteLog["enterPage"]) {
                    petsLog(session, 0, `Login User ${user.account} 進入編輯專案`, projectDetail.project_name);
                    setWroteLog(prev => ({ ...prev, ["enterPage"]: true }))
                }
            }
            // 是否能編輯專案的權限設定
            // 沒有任何系統角色的依照project role
            if (!userPermission.some(p => ['super_admin', 'project_admin', 'group_admin'].includes(p))) {
                if (projectDetail.project_role) {
                    // console.log(`project role of ${projectDetail.project_name}`, projectDetail.project_role.filter((pr) => pr.member_id === user.id));
                    if (projectDetail.project_role.filter((pr) => pr.member_id === user.id)[0].project_role === 5) {
                        setCanEditProject(false);
                    }
                }
            } else {
                // 有系統角色 如果是super admin一律可以編輯專案
                if (userPermission.includes('super_admin')) {
                    setCanEditProject(true);
                } else {
                    // 如果是group admin或是project admin，依照project role
                    if (projectDetail.project_role) {
                        // console.log(`project role of ${projectDetail.project_name}`, projectDetail.project_role.filter((pr) => pr.member_id === user.id));
                        if (projectDetail.project_role.filter((pr) => pr.member_id === user.id)[0].project_role === 5) {
                            setCanEditProject(false);
                        }
                    }
                }

            }
        }
    }, [projectDetail, userPermission])

    // useEffect(() => {
    //     getProjectMembers(projectDetail);
    // }, [projectDetail])

    // Preprocess API part 1
    // console.log('projectDetail', projectDetail);
    var processedProjectDetail = preprocessAPI(projectDetail);
    // console.log("processedProjectDetail\n", processedProjectDetail);

    // Preprocess API part 2 - view
    const columnSettingContentForView = processedProjectDetail => {
        if (processedProjectDetail['Join_func']) {
            let content = [];
            processedProjectDetail['Join_func'].map((cm, index) => {
                // console.log('---', index, processedProjectDetail['Join_func'].length);
                content.push(
                    <>
                        <Grid container item spacing={3}>
                            <Grid container spacing={12}>
                                <Grid item lg={2} />
                                <Grid item lg={8}>
                                    <ColumnConnect columnsMappingList={cm['link_col']} />
                                </Grid>
                            </Grid>
                        </Grid>
                        {/*<Divider />*/}
                        {index < processedProjectDetail['Join_func'].length && (
                            <Grid container item>
                                <Divider light />
                            </Grid>
                        )}
                    </>
                )
            })
            return content;
        }
    };
    //  Preprocess API part 2 - edit
    const handleDelete = async (index) => {
        await setColumnSettingCount(columnSettingCount - 1);
        const newDataConnections = [
            ...dataConnectSettings.slice(0, index),
            ...dataConnectSettings.slice(index + 1)
        ];
        await setDataConnectSettings(newDataConnections);
    }
    const renderColumnSettingContentForEdit = ({ columnSettingCount, dataConnectSettings }) => {
        console.log('dataConnectSettings in columnSettingContent', columnSettingCount, dataConnectSettings);
        let dataConnectSettingsTemp = [...dataConnectSettings];
        let content = [];
        for (let i = 0; i < columnSettingCount; i++) {
            if (!dataConnectSettingsTemp[i]) {
                dataConnectSettingsTemp.push({ left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' });
            }
            // console.log('dataConnectSettings after push', dataConnectSettingsTemp);

            content.push(
                <Grid container item spacing={3}>
                    <Grid container spacing={12}>
                        <Grid item lg={2} />
                        <Grid item lg={8}>
                            <Stack direction='row' spacing={2}>
                                <ConnectSetting dataConnections={dataConnectSettingsTemp} setDataConnections={setDataConnectSettings} index={i} />
                                <IconButton>
                                    <RemoveCircleOutlineIcon sx={{ 'position': "relative", 'top': "-1px" }} onClick={() => handleDelete(i)} />
                                </IconButton>
                            </Stack>
                        </Grid>
                    </Grid>
                </Grid>
            )
        }
        setColumnSettingContent(content);
        return content;
    };

    useEffect(() => {
        // console.log('render cs', dataConnectSettings);
        renderColumnSettingContentForEdit({ columnSettingCount, dataConnectSettings })
    }, [columnSettingCount, dataConnectSettings])

    // Group
    useEffect(() => {
        // get project member options
        let optionsTemp = [];
        allUsers
            .filter((gm) => {
                // 單位下啟用且未被停權的人員
                return gm.group_name === selectedGroup.split('_')[1] && gm.ischange && gm.isactive && gm.id !== user.id;
            })
            .map((pm) => {
                optionsTemp.push({ id: pm.id, label: pm.username + '    ' + pm.email });
            })
        setSelectedMember(null);
        setSelectedMemberId(null);
        setMemberOptions(optionsTemp);
    }, [selectedGroup])

    useEffect(() => {
        // console.log('ori BasicAutocomplete');
        setUserSelectAutocomplete(<BasicAutocomplete options={memberOptions} inputValue={selectedMember} setInputValue={setSelectedMember} setSelectedId={setSelectedMemberId} fullWidth />)
    }, [selectedGroup, memberOptions])

    const columns = useMemo(() => {
        let columns = [
            {
                Header: '主責單位',
                accessor: 'group_name',
                className: 'cell-center',
            },
            {
                Header: '使用者姓名',
                accessor: 'user_name',
                className: 'cell-center',
                disableSortBy: true,
            },
            {
                Header: '使用者信箱',
                accessor: 'user_email',
                className: 'cell-center',
                disableSortBy: true,
            },
            {
                Header: '角色',
                accessor: 'user_role',
                className: 'cell-center',
                disableSortBy: true,
            },
        ]
        if (canEditProject) {
            columns.push({
                Header: '刪除',
                className: 'delete',
                disableSortBy: true,
                Cell: ({ row }) => ActionsCell(row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles)
            })
        }
        return columns;
    }, [theme, projectMembers, projectRoles, canEditProject])

    /* handle functions */
    const handleClose = () => {
        console.log('close');
    };

    function getProjectUpdatePayload() {
        console.log('projectDetail', projectDetail);
        console.log(projectRoles);
        const payload = JSON.parse(JSON.stringify(projectDetail));;
        payload['join_func'] = dataConnectSettings;
        payload['group_id'] = router.query.project_group_id;
        payload['join_type'] = join_method_dic[dataJoinMethod];
        delete payload.Join_func;
        payload.project_role = projectRoles;
        return payload;
    }

    // Edit mode to update project data
    const handleCheck = async () => {
        let temp = [];
        await Promise.all(
            await dataConnectSettings.map(async (dc) => {
                console.log('dc', dc);
                if (dc['left_datasetname'] === '' || dc['left_col'] === '' || dc['right_datasetname'] === '' || dc['right_col'] === '') {
                    await setPopUpMsg('資料鏈結不可以為空');
                    await setCheckPopUp(true);
                    await temp.push(false);
                } else {
                    await temp.push(true);
                }
            })
        )
        return temp;
    }
    // 儲存設定type為save，回到專案列表頁面; 鏈結設定檢查去資料檢查頁面
    const handleSave = async (type = 'save') => {
        // Fetch API /projects/update
        let checker = arr => arr.every(v => v === true);
        const goSave = await handleCheck();
        console.log('goSave', goSave, checker(goSave));
        if (checker(goSave)) {
            const url = "/api/project/put_projectUpdate";
            // const payload = projectUpdatePayload; // [TODO] need to fill in dynamic data
            const payload = getProjectUpdatePayload();
            console.log('update payload', payload);
            const config = { headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` }, };
            const promiseResult = await axiosPlus({ method: "PUT", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false });
            console.log("API /projects/update response:\n", promiseResult);
            if (!wroteLog["editProject"]) {
                petsLog(session, 0, `Login User ${user.account} 編輯專案`, processedProjectDetail.project_name);
                setWroteLog(prev => ({ ...prev, ["editProject"]: true }))
            }
            if (type === 'save') {
                // Go back to projects-table
                router.push('/apps/project/projects-table');
            } else {
                // Go to data-check
                router.push(`/apps/project/data-check?project_id=${project_id}&project_name=${processedProjectDetail.project_name}`)
            }

        }
    }

    const handleEnckey = async () => {
        // Fetch API /projects/list
        const config = { headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` }, };
        const promiseResult = await axiosPlus({
            method: "GET",
            stateArray: null,
            url: "/api/project/get_projectGenkey",
            config: config,
            showSuccessMsg: false,
        });
        // console.log("promiseResult.data.enc_key:", promiseResult.data.enc_key);

        // Update enckey state
        setEnckey(promiseResult.data.enc_key);
    };

    const handleGroupSelect = (event) => {
        setSelectedGroup(event.target.value);
    };

    const handleUserRoleSelect = (event) => {
        setSelectedUserRole(event.target.value);
    };

    const handleAddMember = async () => {
        let id = selectedMemberId;
        let name = selectedMember.split(' ')[0];
        let email = selectedMember.split(' ')[1];
        let groupId = selectedGroup.split('_')[0];
        let groupName = selectedGroup.split('_')[1];

        await setProjectMembers(current =>
            [...current, {
                'group_id': groupId, 'group_name': groupName,
                'member_id': id, 'user_name': name, 'user_email': email,
                'user_role': selectedUserRole, 'user_role_id': member_roles_id_dic[selectedUserRole]
            }]);
        await setProjectRoles(current =>
            [...current, { 'member_id': id, 'group_id': groupId, 'member_role': member_roles_id_dic[selectedUserRole] }])
    };

    const handleJoinMethodSelect = (event) => {
        setDataJoinMethod(event.target.value);
    }

    const downloadKey = (saveObj) => {
        if (keyDownload || firstDownload) {
            // console.log('download');
            const text = JSON.stringify(saveObj);
            const name = "key.json";
            const type = "text/plain";
            // create file
            const a = document.createElement("a");
            const file = new Blob([text], { type: type });
            a.href = URL.createObjectURL(file);
            a.download = name;
            document.body.appendChild(a);
            a.click();
            a.remove();
        }
    }

    return (
        <Page title="Customer List">
            {/*<MainCard content={false}>*/}
            {/* 頂部進度條 */}
            <Box sx={{ width: '750px',  margin:"20px auto 60px auto" }} >
                <Box sx={{ width: "100%", alignItems: "center" }} >
                    <ProjectStepper currentStep={projectStatus} terminatedStep={null} />
                </Box>
            </Box>

            <Box>
                <Grid container spacing={6} sx={{ ml: "50px" }}>
                    <Grid container item>
                        <Grid item>
                            <Stack>
                                <Typography variant='h3'>
                                    查看專案及設定
                                </Typography>
                                <Divider />
                            </Stack>
                        </Grid>
                    </Grid>

                    <Grid container item spacing={3}>
                        <Grid container spacing={12} >
                            <Grid item lg={2}>
                                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案名稱</InputLabel>
                            </Grid>
                            <Grid item lg={8}>
                                <TextField
                                    fullWidth
                                    value={processedProjectDetail.project_name}
                                    InputProps={{ readOnly: true, disableUnderline: true }}
                                    disabled
                                    variant="filled"
                                    sx={{
                                        "& .MuiInputBase-input.Mui-disabled": {
                                            backgroundColor: "disableBGColor",
                                            WebkitTextFillColor: "#000000",
                                            padding: "10px"
                                        }
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid>
                        <Divider light />
                    </Grid>

                    <Grid container item spacing={3}>
                        <Grid container spacing={12} >
                            <Grid item lg={2}>
                                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案資料夾</InputLabel>
                            </Grid>
                            <Grid item lg={8}>
                                <TextField
                                    fullWidth
                                    value={processedProjectDetail.project_eng}
                                    InputProps={{ readOnly: true, disableUnderline: true }}
                                    disabled
                                    variant="filled"
                                    sx={{
                                        "& .MuiInputBase-input.Mui-disabled": {
                                            backgroundColor: "disableBGColor",
                                            WebkitTextFillColor: "#000000",
                                            padding: "10px"
                                        }
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </Grid>

                    <Grid container item spacing={3}>
                        <Grid container spacing={12} >
                            <Grid item lg={2}>
                                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left' } }}>金鑰</InputLabel>
                            </Grid>

                            <Grid item lg={8}>
                                <TextField
                                    fullWidth
                                    value={(enckey) ? enckey : processedProjectDetail.enc_key}
                                    InputProps={{ readOnly: true, disableUnderline: true }}
                                    disabled
                                    multiline
                                    variant="filled"
                                    sx={{
                                        "& .MuiInputBase-colorPrimary.Mui-disabled": {
                                            backgroundColor: "disableBGColor",
                                            // padding: "10px"
                                        },
                                        "& .MuiInputBase-input.Mui-disabled": {
                                            WebkitTextFillColor: "#000000",
                                        }
                                    }}
                                // onChange={handleEnckey}
                                />
                            </Grid>
                            <Grid item lg={2}>
                                <Button onClick={() => {
                                    setFirstDownload(false);
                                    setKeydownload(true);
                                    downloadKey({ "enc_key": processedProjectDetail.enc_key })
                                }} variant="text" startIcon={<FileDownloadOutlinedIcon />} >下載</Button>
                            </Grid>
                            {/*<Grid item lg={2}>*/}
                            {/*    <Button variant="contained" fullWidth onClick={handleEnckey}>產生新金鑰</Button>*/}
                            {/*</Grid>*/}
                        </Grid>
                    </Grid>

                    {canEditProject && (
                        <Grid container item spacing={3}>
                            <Grid container spacing={6}>
                                <Grid item lg={2}>
                                    <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left' } }}>選擇協作人員</InputLabel>
                                </Grid>
                                <Grid container item lg={8} spacing={1}>
                                    <Grid item md={3} lg={3}>
                                        <Select
                                            value={selectedGroup}
                                            displayEmpty
                                            name="select group name"
                                            renderValue={(selected) => {
                                                return selected.split('_')[1];;
                                            }}
                                            fullWidth
                                            onChange={handleGroupSelect}
                                        >
                                            {allGroups.map((g) => {
                                                return <MenuItem value={`${g.id}_${g.group_name}`}>{g.group_name}</MenuItem>
                                            })}
                                        </Select>
                                    </Grid>
                                    <Grid item md={6} lg={6}>
                                        {userSelectAutocomplete}
                                        {/*<BasicAutocomplete options={memberOptions} inputValue={selectedMember} setInputValue={setSelectedMember} setSelectedId={setSelectedMemberId} fullWidth />*/}
                                    </Grid>
                                    <Grid item md={3} lg={3}>
                                        <Select
                                            value={selectedUserRole}
                                            displayEmpty
                                            name="select user role"
                                            renderValue={(selected) => {
                                                return selected;
                                            }}
                                            fullWidth
                                            onChange={handleUserRoleSelect}
                                        >
                                            {member_roles.map((mr) => {
                                                return <MenuItem value={mr}>{mr}</MenuItem>
                                            })}

                                        </Select>
                                    </Grid>
                                </Grid>
                                <Grid item lg={2}>
                                    <Button variant="outlined" fullWidth onClick={handleAddMember}>新增</Button>
                                </Grid>
                            </Grid>
                        </Grid>
                    )}

                    <Grid container item spacing={3}>
                        <Grid container spacing={6}>
                            <Grid item lg={2} />
                            <Grid item lg={8}>
                                <MainCard content={false}>
                                    <ScrollX>
                                        <ReactTable columns={columns} data={projectMembers} />
                                    </ScrollX>
                                </MainCard>
                            </Grid>
                        </Grid>
                    </Grid>

                    <Grid container item spacing={3}>
                        <Grid container spacing={12} >
                            <Grid item lg={2}>
                                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>服務端網域名稱</InputLabel>
                            </Grid>
                            <Grid item lg={8}>
                                <TextField
                                    fullWidth
                                    value={window.location.hostname}
                                    InputProps={{ readOnly: true, disableUnderline: true }}
                                    disabled
                                    variant="filled"
                                    sx={{
                                        "& .MuiInputBase-input.Mui-disabled": {
                                            backgroundColor: "disableBGColor",
                                            WebkitTextFillColor: "#000000",
                                            padding: "10px"
                                        }
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </Grid>

                    <Grid container item spacing={3}>
                        <Grid container spacing={12} >
                            <Grid item lg={2}>
                                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>服務端目錄名稱</InputLabel>
                            </Grid>
                            <Grid item lg={8}>
                                <TextField
                                    fullWidth
                                    value={window.location.pathname}
                                    InputProps={{ readOnly: true, disableUnderline: true }}
                                    disabled
                                    variant="filled"
                                    sx={{
                                        "& .MuiInputBase-input.Mui-disabled": {
                                            backgroundColor: "disableBGColor",
                                            WebkitTextFillColor: "#000000",
                                            padding: "10px"
                                        }
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </Grid>

                    <Grid container item spacing={3}>
                        <Grid container spacing={12}>
                            <Grid item lg={2}>
                                <Typography fullWidth multiline sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>資料鏈結方式</Typography>
                            </Grid>
                            {canEditProject ? (
                                <Grid item lg={4}>
                                    <Select
                                        fullWidth
                                        value={dataJoinMethod}
                                        displayEmpty
                                        name="select data connect method"
                                        renderValue={(selected) => {
                                            return selected;
                                        }}
                                        onChange={handleJoinMethodSelect}
                                    >
                                        <MenuItem value={'Full outer join'}>Full outer join</MenuItem>
                                        <MenuItem value={'Inner join'}>Inner join</MenuItem>
                                    </Select>
                                </Grid>
                            ) : (
                                <Grid item lg={8}>
                                    <TextField
                                        fullWidth
                                        value={dataJoinMethod}
                                        InputProps={{ readOnly: true, disableUnderline: true }}
                                        disabled
                                        variant="filled"
                                        sx={{
                                            "& .MuiInputBase-input.Mui-disabled": {
                                                backgroundColor: "disableBGColor",
                                                WebkitTextFillColor: "#000000",
                                                padding: "10px"
                                            }
                                        }}
                                    />
                                </Grid>
                            )}
                        </Grid>
                    </Grid>

                    <Grid container item spacing={3}>
                        <Grid container spacing={12}>
                            <Grid item xs={2}>
                                <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>資料鏈結欄位屬性設定</Typography>
                            </Grid>

                            {/*<Grid item xs={6}>*/}
                            {/*    <ConnectSetting start={true}/>*/}
                            {/*</Grid>*/}
                        </Grid>
                    </Grid>
                    {/*<Divider />*/}
                    {!canEditProject && (columnSettingContentForView(processedProjectDetail))}
                    {(canEditProject && dataConnectSettings && dataConnectSettings[0].left_datasetname !== '') && (
                        columnSettingContent
                    )}
                    {/*{isDataProvider && (columnSettingContentForView(processedProjectDetail))}*/}
                    {/*{(!isDataProvider && dataConnectSettings && dataConnectSettings[0].left_datasetname !== '') && (*/}
                    {/*    columnSettingContent*/}
                    {/*    // renderColumnSettingContentForEdit({ columnSettingCount, dataConnectSettings })*/}
                    {/*    // columnSettingContentForEdit({ columnSettingCount, dataConnectSettings })*/}
                    {/*)}*/}
                </Grid>
            </Box>

            {canEditProject && (
                <Box
                    m={1}
                    display="flex"
                    justifyContent="flex-end"
                    alignItems="flex-end"
                >
                    <Button variant="outlined" onClick={() => { setColumnSettingCount(columnSettingCount + 1) }} startIcon={<AddIcon />} />
                </Box>
            )}

            {/*<Box*/}
            {/*    m={1}*/}
            {/*    display="flex"*/}
            {/*    justifyContent="flex-end"*/}
            {/*    alignItems="flex-end"*/}
            {/*>*/}
            {/*    <Button*/}
            {/*        variant="contained"*/}
            {/*        onClick={() => { router.push('/apps/project/projects-table'); }}*/}
            {/*    >*/}
            {/*        回到專案列表*/}
            {/*    </Button>*/}
            {/*</Box>*/}

            {canEditProject && (
                <>
                    <Box
                        m={1}
                        display="flex"
                        justifyContent="flex-end"
                        alignItems="flex-end"
                    >
                        <Button variant="contained" onClick={() => handleSave('save')}>
                            儲存設定
                        </Button>
                    </Box>
                    <Box
                        m={1}
                        display="flex"
                        justifyContent="flex-end"
                        alignItems="flex-end"
                    >
                        <Button
                            variant="contained"
                            onClick={() => handleSave('check')}
                        >
                            資料匯入及鍵結設定檢查
                        </Button>
                    </Box>
                </>
            )}

            <Dialog open={checkPopUp} onClose={() => { setCheckPopUp(false) }}>
                <DialogTitle>
                    {popUpMsg}
                </DialogTitle>
            </Dialog>
            {/*</MainCard>*/}
        </Page>
    );
};

EditProject.getLayout = function getLayout(page) {
    return <Layout>{page}</Layout>;
};

export default EditProject;
