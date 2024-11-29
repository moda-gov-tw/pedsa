import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import ClearIcon from '@mui/icons-material/Clear';
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Divider,
  IconButton,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

// third-party
import axios from 'axios';
import { useExpanded, useFilters, useGlobalFilter, usePagination, useRowSelect, useSortBy, useTable } from 'react-table';

// project import
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import { HeaderSort, TableRowSelection } from 'components/third-party/ReactTable';
import { ConfigContext } from 'contexts/ConfigContext';
import { id_to_join_method_dic, join_method_dic } from 'data/join-method';
import { member_roles, member_roles_id_dic, roles_id_member_dic } from 'data/member-role';
import useUser from 'hooks/useUser';
import petsLog from 'sections/apps/logger/insert-system-log';
import BasicAutocomplete from 'sections/components-overview/autocomplete/BasicAutocomplete';
import getALLGroups from 'utils/getGroups';
import getALLUsers from 'utils/getUsers';
import { renderFilterTypes } from 'utils/react-table';

// ==============================|| API ||============================== //
/**
 * handleGetProjectDetail
 * API: fetch project detail
 * @param {any} session
 * @param {String} project_id
 * @param {Array} returnColumnFilterList
 * String of array. 填入 projectDetail 的 key，可使 return object 只包含 returnColumnFilterList 所過濾的的資料
 * @param {any} setProjectDetail
 * Hook state. 將過濾結果存入 state
 * @param {Boolean} preprocessJoinFunc
 * Default false. 是否對 join_func 做前處理. if true, 處理後的 join_func 存於 new key "Join_func"
 * @returns {Object} Object of filterd projectDetail
 */
const handleGetProjectDetail = async (
  session,
  project_id,
  returnColumnFilterList = [],
  setProjectDetail = null,
  preprocessJoinFunc = false
) => {
  const payload = {
    project_id: project_id
  };
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  const promiseResult = await axiosPlus({
    method: 'POST',
    stateArray: null,
    url: '/api/project/post_projectDetail',
    payload: payload,
    config: config,
    showSuccessMsg: false
  });
  var returnObject = {};
  if (promiseResult.status == 200 && promiseResult.data.status == true) {
    const projectDetailObject = promiseResult.data.obj;

    // If ColumnFilterList exists, filter promiseResult and return the object of key-value pairs.
    if (returnColumnFilterList.length > 0) {
      returnColumnFilterList.forEach((keyColumn) => {
        returnObject[keyColumn] = projectDetailObject[keyColumn];
      });
    } else {
      returnObject = projectDetailObject;
    }
  } else {
    console.log('POST projectDetail fail', promiseResult);
    returnObject = null;
  }

  if (preprocessJoinFunc && returnObject && returnObject.join_func.length > 0) {
    returnObject = {
      ...returnObject,
      Join_func: returnObject['join_func'].map((cell, index) => ({
        link_col: [cell.left_datasetname, cell.left_col, cell.right_datasetname, cell.right_col]
      }))
    };
  }

  if (setProjectDetail) setProjectDetail(returnObject);

  return returnObject;
};

// API: fetch project status (/api/projects/status)
const handleFetchProjectStatus = async (session, project_id, setProjectStatus) => {
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    },
    params: {
      project_id: project_id
    }
  };
  const promiseResult = await axiosPlus({
    method: 'GET',
    stateArray: null,
    url: '/api/project/get_projectStatus',
    config: config,
    showSuccessMsg: false
  });

  if (promiseResult && promiseResult?.status == 200) setProjectStatus(promiseResult.data.obj.status);
};

// API: set new project status
const handleSetProjectStatus = async (session, project_id, newStatus) => {
  const payload = {
    project_id: project_id,
    status: newStatus
  };
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  const promiseResult = await axiosPlus({
    method: 'PUT',
    stateArray: null,
    url: '/api/project/put_projectStatus',
    payload: payload,
    config: config,
    showSuccessMsg: false
  });

  if (promiseResult.status == 200 && promiseResult.data.status == true) {
    console.log('PUT projectStatus success');
  } else console.log('PUT projectStatus fail', promiseResult);
};

// API: get joined sample data
const getSampleData = async (token, project_id, setSampledata, showLength = null) => {
  // Send a POST request
  const promiseResult = await axios({
    method: 'post',
    url: '/api/project/post_sample',
    data: { project_id: project_id },
    config: {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  });

  if (promiseResult.status == 200 && promiseResult.data.status === 0) {
    // console.log("POST API projects/sample success");
    const parsedObject = JSON.parse(promiseResult.data.obj.join_sampledata);
    if (parsedObject) {
      if (showLength != null && showLength > 0) setSampledata(parsedObject.slice(0, showLength));
      else setSampledata(parsedObject);
    }
  } else console.log('POST API projects/sample fail', promiseResult);
};

// API: reset project status to 1
const handleProjectReset = async (session, project_id) => {
  // Current project_id
  console.log(`Reset project_id = ${project_id}`);
  // API /projects/reset
  const url = '/api/project/put_projectReset';
  const payload = { project_id: project_id };
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  const promiseResult = await axiosPlus({
    method: 'PUT',
    stateArray: null,
    url: url,
    payload: payload,
    config: config,
    showSuccessMsg: false
  });

  if (promiseResult.status == 200 && promiseResult.data.status == true && promiseResult.data.status == true) {
    console.log('PUT projectReset success');
    return true;
  } else {
    console.log('PUT projectReset fail', promiseResult);
    return false;
  }
};

// API: fetch sub-system status (/api/project/get_x_checkstatus)
const handleFetchSubSystemStatus = async (session, project_eng, url, whom) => {
  const config = {
    headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
    params: { project_name: project_eng }
  };

  const promiseResult = await axiosPlus({
    method: 'GET',
    stateArray: null,
    url: url,
    config: config,
    showSuccessMsg: false
  });

  if (promiseResult.status == 200) {
    if (promiseResult.data[0].status == 1) {
      // console.log("API checkstatus success");
      return promiseResult.data[0].obj;
    } else {
      console.log(`子系統_${whom} 專案名稱 ${project_eng} 不存在 (或是專案正在建立中):`, promiseResult);
      return { project_status: -1 };
    }
  }
  // API REQUESTF ERROR: axiosPlus would catch and log
  else console.log(`子系統_${whom} 專案名稱 ${project_eng}\nRequest API ERROR`, promiseResult);
  return { project_status: 0 };
};

// API: reset sub-system status (/api/project/get_x_reset)
const handleResetSubSystemStatus = async (session, projectEng, subsystemProjectID, whom) => {
  const subsystemConfig = {
    KAnonymous: { queryParam: 'k_project_id', requestURL: '/api/project/get_k_reset' },
    syntheticData: { queryParam: 'syn_project_id', requestURL: '/api/project/get_syn_reset' },
    differentialPrivacy: { queryParam: 'dp_project_id', requestURL: '/api/project/get_dp_reset' }
  };

  const requestProps = {
    method: 'GET',
    stateArray: null,
    url: subsystemConfig[whom].requestURL,
    config: {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
      params: { project_name: projectEng }
    },
    showSuccessMsg: false
  };
  requestProps.config.params[subsystemConfig[whom].queryParam] = subsystemProjectID;
  const promiseResult = await axiosPlus(requestProps);

  if (promiseResult.status == 200 && promiseResult.data[0].status == 1) {
    console.log('GET sub-system reset project success');
  } else {
    console.log('ResetSubSystemStatus send data', requestProps);
    console.log('GET sub-system reset project fail', promiseResult);
  }

  return promiseResult;
};

// ==============================|| REACT TABLE ||============================== //
function ReactTable({ columns, data }) {
  const theme = useTheme();
  const router = useRouter();
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
    setGlobalFilter
  } = useTable(
    {
      columns,
      data,
      filterTypes,
      initialState: {
        pageIndex: 0,
        pageSize: 10,
        sortBy: [sortBy],
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
              <TableRow {...headerGroup.getHeaderGroupProps()} key={index} sx={{ '& > th:first-of-type': { width: '40px' } }}>
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
  handleAdd: PropTypes.func
};

const ActionsCell = (row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles) => {
  async function handleRemoveMember() {
    let index1 = projectMembers.findIndex(function (temp) {
      return temp.member_id === row.original.member_id;
    });
    const newProjectMembers = [...projectMembers.slice(0, index1), ...projectMembers.slice(index1 + 1)];
    let index2 = projectRoles.findIndex(function (temp) {
      return temp.member_id === row.original.member_id;
    });
    const newProjectRoles = [...projectRoles.slice(0, index2), ...projectRoles.slice(index2 + 1)];

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

// ==============================|| Edit Project Member COMPONENT ||============================== //
/**
 * Function: EditProjectMember
 *
 * 可以編輯協作人員的對話框
 *
 * @param {{ projectDetail: Object, onCancel: Function }} argObject
 * @returns {JSX.Element}
 */
const EditProjectMember = ({ projectDetail, onCancel }) => {
  const { data: session } = useSession();
  const user = useUser();
  const theme = useTheme();

  const [popUp, setPopUp] = useState(false);
  const [popUpMessage, setPopUpMessage] = useState('');
  const router = useRouter();
  const { allUsers, setAllUsers, allGroups, setAllGroups, userPermission } = useContext(ConfigContext); // 所有單位、人員

  const [userInfo, setUserInfo] = useState(null);
  const [dataJoinMethod, setDataJoinMethod] = useState('Inner join');

  const [selectedGroup, setSelectedGroup] = useState('機關A'); //選擇專案成員單位
  const [memberOptions, setMemberOptions] = useState([]); //機關下成員選項
  const [selectedMember, setSelectedMember] = useState(null);
  const [selectedMemberId, setSelectedMemberId] = useState(null);
  const [selectedUserRole, setSelectedUserRole] = useState('專案使用者'); //選擇專案成員角色

  const [projectMembers, setProjectMembers] = useState([]); //專案成員表格資料
  const [projectRoles, setProjectRoles] = useState([]); // member_role

  const [dataConnectSettings, setDataConnectSettings] = useState([
    { left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' }
  ]);
  const [columnSettingCount, setColumnSettingCount] = useState(2);
  const [checkPopUp, setCheckPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [userSelectAutocomplete, setUserSelectAutocomplete] = useState(
    <BasicAutocomplete
      options={memberOptions}
      inputValue={selectedMember}
      setInputValue={setSelectedMember}
      setSelectedId={setSelectedMemberId}
      fullWidth
    />
  );
  const [wroteLog, setWroteLog] = useState({});

  useEffect(() => {
    // Get user info
    getUserInfo(session.tocken.loginUserToken);
    // console.log('project_group_id', router.query.project_group_id);
    getALLGroups(setAllGroups, session.tocken.loginUserToken); // get all groups
    getALLUsers(setAllUsers, session.tocken.loginUserToken); // get all users

    if (projectDetail) {
      setDataJoinMethod(id_to_join_method_dic[Number(projectDetail.join_type)]);
      getOriDataConnectSettings(projectDetail);
      getProjectMembers(projectDetail);
    }
  }, []);

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
      });
    setSelectedMember(null);
    setSelectedMemberId(null);
    setMemberOptions(optionsTemp);
  }, [selectedGroup]);

  useEffect(() => {
    setUserSelectAutocomplete(
      <BasicAutocomplete
        options={memberOptions}
        inputValue={selectedMember}
        setInputValue={setSelectedMember}
        setSelectedId={setSelectedMemberId}
        fullWidth
      />
    );
  }, [selectedGroup, memberOptions]);

  const getUserInfo = async (token) => {
    const url = `/api/user/get_info/${user.id}`;
    const config = {
      headers: {
        Authorization: `Bearer ${token}`
      }
    };
    const userInfoTemp = await axios.get(url, config);
    setUserInfo(userInfoTemp.data.obj);
  };

  function getOriDataConnectSettings(projectDetail) {
    let oriDataConnectSettings = [];
    if (projectDetail['join_func']) {
      let joinfunc_array = projectDetail['join_func'];
      for (let i = 0; i < joinfunc_array.length; i++) {
        oriDataConnectSettings.push({
          left_datasetname: joinfunc_array[i].left_datasetname,
          left_col: joinfunc_array[i].left_col,
          right_datasetname: joinfunc_array[i].right_datasetname,
          right_col: joinfunc_array[i].right_col
        });
      }
      console.log('oriDataConnectSettings', oriDataConnectSettings);
      setColumnSettingCount(joinfunc_array.length);
      setDataConnectSettings(oriDataConnectSettings);
    }
  }

  // get project members
  async function getProjectMembers(projectDetail) {
    console.log('get project members', projectDetail['project_role']);
    let projectMembersList = [];
    let projectMemberRolesList = [];
    if (projectDetail['project_role']) {
      await Promise.all(
        await projectDetail.project_role.map(async (pmr) => {
          await axios
            .get(`/api/user/get_info/${pmr.member_id}`, {
              headers: {
                Authorization: `Bearer ${session.tocken.loginUserToken}`
              }
            })
            .then(async (res) => {
              console.log('get project members', res);
              let temp = {};
              temp['member_id'] = pmr.member_id;
              temp['member_role'] = pmr.project_role;
              temp['user_role'] = roles_id_member_dic[pmr.project_role];
              temp['group_id'] = res.data.obj.group_id;
              temp['group_name'] = res.data.obj.group_name;
              temp['user_name'] = res.data.obj.username;
              temp['user_email'] = res.data.obj.email;
              // console.log('temp', temp);
              projectMembersList.push(temp);
              projectMemberRolesList.push({
                member_id: pmr.member_id,
                group_id: res.data.obj.group_id,
                member_role: pmr.project_role
              });
            })
            .catch((error) => {
              // console.log('get project members', error);
            });
        })
      );
      console.log('projectMembersList', projectMembersList);
      setProjectMembers(projectMembersList);
      setProjectRoles(projectMemberRolesList);
    }
  }

  const columns = useMemo(() => {
    let columns = [
      {
        Header: '主責單位',
        accessor: 'group_name',
        className: 'cell-center'
      },
      {
        Header: '使用者姓名',
        accessor: 'user_name',
        className: 'cell-center',
        disableSortBy: true
      },
      {
        Header: '使用者信箱',
        accessor: 'user_email',
        className: 'cell-center',
        disableSortBy: true
      },
      {
        Header: '角色',
        accessor: 'user_role',
        className: 'cell-center',
        disableSortBy: true
      }
    ];
    columns.push({
      Header: '刪除',
      className: 'delete',
      disableSortBy: true,
      Cell: ({ row }) => ActionsCell(row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles)
    });
    return columns;
  }, [theme, projectMembers, projectRoles]);

  function getProjectUpdatePayload() {
    console.log('projectDetail', projectDetail);
    console.log(projectRoles);
    const payload = JSON.parse(JSON.stringify(projectDetail));
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
    );
    return temp;
  };
  // 儲存設定type為save，回到專案列表頁面; 鏈結設定檢查去資料檢查頁面
  const handleSave = async (type = 'save') => {
    // Fetch API /projects/update
    let checker = (arr) => arr.every((v) => v === true);
    const goSave = await handleCheck();
    console.log('goSave', goSave, checker(goSave));
    if (checker(goSave)) {
      const url = '/api/project/put_projectUpdate';
      // const payload = projectUpdatePayload; // [TODO] need to fill in dynamic data
      const payload = getProjectUpdatePayload();
      console.log('update payload', payload);
      const config = { headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` } };
      let promiseResult;
      try {
        promiseResult = await axios.post(url, payload, config);
      } catch (error) {
        promiseResult = error.response;
      }
      // const promiseResult = await axiosPlus({ method: "PUT", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false });
      console.log('API /projects/insert response/error:\n', promiseResult);
      if (promiseResult.status === 400) {
        await setPopUpMsg(promiseResult.data.msg);
        await setCheckPopUp(true);
      }

      if (!wroteLog['editProject']) {
        await petsLog(session, 0, `Login User ${user.account} 編輯協作人員`, projectDetail.project_name);
        setWroteLog((prev) => ({ ...prev, ['editProject']: true }));
      }
      if (promiseResult.status === 200) {
        onCancel();
      }
    }
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

    await setProjectMembers((current) => [
      ...current,
      {
        group_id: groupId,
        group_name: groupName,
        member_id: id,
        user_name: name,
        user_email: email,
        user_role: selectedUserRole,
        user_role_id: member_roles_id_dic[selectedUserRole]
      }
    ]);
    await setProjectRoles((current) => [
      ...current,
      { member_id: id, group_id: groupId, member_role: member_roles_id_dic[selectedUserRole] }
    ]);
  };

  return (
    <>
      <DialogTitle>編輯協作人員</DialogTitle>
      <Divider />
      <DialogContent>
        {projectDetail && (
          <Stack direction="column" spacing={1}>
            <Stack direction="row">
              <Box sx={{ width: '25%' }}>
                <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                  專案名稱
                </Typography>
              </Box>
              <Box sx={{ width: '75%' }}>
                <TextField
                  fullWidth
                  value={projectDetail.project_name}
                  InputProps={{ readOnly: true, disableUnderline: true }}
                  disabled
                  variant="filled"
                  sx={{
                    '& .MuiInputBase-input.Mui-disabled': {
                      backgroundColor: 'disableBGColor',
                      WebkitTextFillColor: '#000000',
                      padding: '10px'
                    }
                  }}
                />
              </Box>
            </Stack>

            <Stack direction="row">
              <Box sx={{ width: '25%' }}>
                <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                  專案資料夾
                </Typography>
              </Box>
              <Box sx={{ width: '75%' }}>
                <TextField
                  fullWidth
                  value={projectDetail.project_eng}
                  InputProps={{ readOnly: true, disableUnderline: true }}
                  disabled
                  variant="filled"
                  sx={{
                    '& .MuiInputBase-input.Mui-disabled': {
                      backgroundColor: 'disableBGColor',
                      WebkitTextFillColor: '#000000',
                      padding: '10px'
                    }
                  }}
                />
              </Box>
            </Stack>

            {/* 協作人員下拉選單 */}
            <Stack direction="row">
              <Box sx={{ width: '20%' }}>
                <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                  選擇協作人員
                </Typography>
              </Box>

              <Box sx={{ width: '20%' }}>
                <Select
                  value={selectedGroup}
                  displayEmpty
                  name="select group name"
                  renderValue={(selected) => {
                    return selected.split('_')[1];
                  }}
                  fullWidth
                  onChange={handleGroupSelect}
                >
                  {allGroups.map((g) => {
                    return <MenuItem value={`${g.id}_${g.group_name}`}>{g.group_name}</MenuItem>;
                  })}
                </Select>
              </Box>

              <Box sx={{ width: '30%' }}>{userSelectAutocomplete}</Box>

              <Box sx={{ width: '20%' }}>
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
                    return <MenuItem value={mr}>{mr}</MenuItem>;
                  })}
                </Select>
              </Box>

              <Box sx={{ width: '10%' }}>
                <Button variant="outlined" fullWidth onClick={handleAddMember}>
                  新增
                </Button>
              </Box>
            </Stack>

            {/* 協作人員表格 */}
            <Box sx={{ width: '100%' }}>
              <MainCard content={false}>
                <ScrollX>
                  <ReactTable columns={columns} data={projectMembers} />
                </ScrollX>
              </MainCard>
            </Box>

            <Box display="flex" justifyContent="space-evenly">
              <Button variant="outlined" onClick={onCancel}>
                取消變更
              </Button>
              <Button variant="contained" onClick={() => handleSave('save')}>
                儲存設定
              </Button>
            </Box>
          </Stack>
        )}
      </DialogContent>

      {/*提示訊息*/}
      <Dialog open={popUp} onClose={onCancel}>
        <DialogTitle>{popUpMessage}</DialogTitle>
      </Dialog>
    </>
  );
};

EditProjectMember.propTypes = {
  projectDetail: PropTypes.object,
  onCancel: PropTypes.func
};

export default EditProjectMember;
