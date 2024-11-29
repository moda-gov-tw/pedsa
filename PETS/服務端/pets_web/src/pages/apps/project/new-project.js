import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { styled } from '@mui/material/styles';
import Paper from '@mui/material/Paper';
import { useTheme } from '@mui/material/styles';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  Divider,
  Grid,
  IconButton,
  InputLabel,
  Menu,
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
  Typography,
  useMediaQuery,
  FormControl,
  FormLabel,
  FormControlLabel,
  RadioGroup,
  Radio
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';

// third-party
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import { member_roles, member_roles_id_dic } from 'data/member-role';
import useUser from 'hooks/useUser';
import Layout from 'layout';
import Page from 'components/Page';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import { HeaderSort, IndeterminateCheckbox, TableRowSelection } from 'components/third-party/ReactTable';
import BasicAutocomplete from '../../../sections/components-overview/autocomplete/BasicAutocomplete';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import ProjectStepper from 'sections/apps/progress/project_stepper';
import { checkProject, checkProjectFolder } from 'utils/check-rules';
import { checkProjectName, checkProjectEng, checkEmpty } from 'utils/check-project';
// import { handleCheckDuplicatedFolder } from "utils/check-duplicated-folder";

// mock data
import { mockMembers } from '../../../utils/mock-members';
import { mockProjectMembers } from '../../../utils/mock-project-members';
import { mockUserList } from 'utils/mock-users';
import { ConfigContext } from 'contexts/ConfigContext';
import getALLUsers from 'utils/getUsers';
import getALLGroups from '../../../utils/getGroups';
import menuItem from '../../../menu-items';
import StateControlDialog from '../../../sections/apps/Dialog/state-dialog';

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
  const theme = useTheme();
  const router = useRouter();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
  const sortBy = { id: 'fatherName', desc: false };

  async function handleAdd() {
    await router.push('/apps/project/new-project');
  }

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
              <TableRow {...headerGroup.getHeaderGroupProps()} key={index} sx={{ '& > th:first-of-type': { width: '200px' } }}>
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

// ==============================|| ActionsCell ||============================== //
/**
 * Function: ActionsCell
 *
 * Create new project.
 *
 * @param {object} row
 * - Row data of the action cell.
 * @param {array} theme
 * @param {object} projectMembers
 * - Project members add to the project. { 'group_id': groupId, 'group_name': groupName, 'member_id': id, 'user_name': name, 'user_email': email, 'user_role': role, 'user_role_id': roleId }
 * @param {func} setProjectMembers
 * - Function to update projectMembers.
 * @param {object} projectRoles
 * - Project members add to the project. {'member_id': id, 'group_id': groupId, 'member_role': roleId}
 * @param {func} setProjectRoles
 * - Function to update projectRoles.
 *
 * @returns {JSX.Element}
 */
const ActionsCell = (row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles) => {
  // console.log('row in ActionsCell', row);

  async function handleRemoveMember() {
    let index1 = projectMembers.findIndex(function (temp) {
      return temp.member_id === row.original.member_id;
    });
    const newProjectMembers = [...projectMembers.slice(0, index1), ...projectMembers.slice(index1 + 1)];
    let index2 = projectRoles.findIndex(function (temp) {
      return temp.member_id === row.original.member_id;
    });
    const newProjectRoles = [...projectRoles.slice(0, index2), ...projectRoles.slice(index2 + 1)];
    console.log('newProjectRoles', newProjectRoles);

    await setProjectMembers(newProjectMembers);
    await setProjectRoles(newProjectRoles);
  }

  return (
    <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
      <Tooltip title="">
        <IconButton onClick={handleRemoveMember}>
          <ClearIcon />
        </IconButton>
      </Tooltip>
    </Stack>
  );
};

ActionsCell.propTypes = {
  row: PropTypes.object,
  theme: PropTypes.array,
  projectMembers: PropTypes.object,
  setProjectMembers: PropTypes.func,
  projectRoles: PropTypes.object,
  setProjectRoles: PropTypes.func
};

// Section Cell and Header
const SelectionHeader = ({ getToggleAllPageRowsSelectedProps }) => (
  <IndeterminateCheckbox indeterminate {...getToggleAllPageRowsSelectedProps()} />
);

SelectionHeader.propTypes = {
  getToggleAllPageRowsSelectedProps: PropTypes.func
};
// ==============================|| CREATE NEW PROJECT PAGE ||============================== //
/**
 * Function: NewProject
 *
 * @returns {JSX.Element}
 */
const NewProject = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const router = useRouter();
  const user = useUser();
  const { allUsers, setAllUsers, allGroups, setAllGroups } = useContext(ConfigContext); // 所有單位、人員
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };

  const [projectName, setProjectName] = useState(null);
  const [projectFolder, setProjectFolder] = useState(null);
  const [projectGroupId, setProjectGroupId] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState(''); //選擇專案成員單位
  const [members, setMembers] = useState(mockMembers); //所有成員
  const [userOptions, setUserOptions] = useState([]); //機關下成員選項
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState();
  const [selectedUserRole, setSelectedUserRole] = useState('專案使用者'); //選擇專案成員角色
  const [projectMembers, setProjectMembers] = useState([]); //專案成員表格資料
  const [projectRoles, setProjectRoles] = useState([]);
  const [enckey, setEnckey] = useState(''); //金鑰
  const [isSingleDataset, setIsSingleDataset] = useState(0); // 是否為單一資料集
  const [checkPopUp, setCheckPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [userSelectAutocomplete, setUserSelectAutocomplete] = useState(
    <BasicAutocomplete
      options={userOptions}
      inputValue={selectedUser}
      setInputValue={setSelectedUser}
      setSelectedId={setSelectedUserId}
      fullWidth
    />
  );

  // 取得專案建立者資訊
  const getUserInfo = async (token) => {
    console.log('getUserInfo');
    await axios
      .get(`/api/user/get_info/${user.id}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      .then(async (response) => {
        // console.log('get user info', response.data.obj);
        let userInfoTemp = response.data.obj;
        await setUserInfo(response.data.obj);
        if (userInfoTemp.group_id) {
          await setProjectGroupId(userInfoTemp.group_id);
        } else {
          await setProjectGroupId(1);
        }

        // if(projectMembers.length === 0){
        //   await setProjectMembers(current =>
        //         [...current, { 'group_id': userInfoTemp.group_id, 'group_name': userInfoTemp.group_name,
        //           'member_id': user.id, 'user_name': userInfoTemp.username, 'user_email': userInfoTemp.email,
        //           'user_role': '專案管理者', 'user_role_id': member_roles_id_dic['專案管理者']}]);
        // }
        // if(projectRoles.length === 0){
        //   await setProjectRoles(current =>
        //       [...current, {'member_id': user.id, 'group_id': userInfoTemp.group_id, 'member_role': 3}]);
        // }
      })
      .catch((error) => {
        // console.log('get user info error', error);
      });
  };

  useEffect(() => {
    // 取得專案建立者資訊
    getUserInfo(session.tocken.loginUserToken);
    // 取得所有單位
    getALLGroups(setAllGroups, session.tocken.loginUserToken); // get all groups
    // 取得所有使用者
    getALLUsers(setAllUsers, session.tocken.loginUserToken); // get all users
    // setAllUsers(mockUserList);
  }, []);

  function getProjectRolePayload() {
    if (userInfo) {
      let temp = Object.assign([], projectRoles);
      // console.log('temp', temp);
      temp.push({ member_id: user.id, group_id: userInfo.group_id, member_role: 3 });
      return temp;
    }
  }

  async function handleCheck() {
    let msg1 = "";
    let msg2 = "";
    const msgEmpty = await checkEmpty(projectName, projectFolder, setCheckPopUp, setPopUpMsg);
    if (msgEmpty === 'ok') {
      msg1 = await checkProjectName(projectName, config, setCheckPopUp, setPopUpMsg);
      if (msg1 === 'ok') {
        msg2 = await checkProjectEng(projectFolder, config, setCheckPopUp, setPopUpMsg);
      }
    }

    if (msgEmpty === 'ok' && msg1 === 'ok' && msg2 === 'ok') {
      if (projectName && projectFolder && enckey && !checkProject(projectName) && !checkProjectFolder(projectFolder)) {
        return true;
      } else {
        setCheckPopUp(true);
        setPopUpMsg('請確認專案名稱及專案資料夾皆有填入符合格式規範的內容，且金鑰已生成');
      }
    }
  }

  async function handleClick() {
    const goNext = await handleCheck();
    if (goNext) {
      let pr = await getProjectRolePayload();
      router.push({
        pathname: '/apps/project/new-project-data-connect',
        // query: { name: '123', age: '456' },// enc_key: enckey,
        query: {
          project_name: projectName,
          project_eng: projectFolder,
          enc_key: enckey,
          group_id: projectGroupId,
          project_role: JSON.stringify(pr)
        }
      });
    }
  }

  async function handleSave() {
    const goNext = await handleCheck(); // TODO: 檢查單一資料集還沒更改
    if (goNext) {
      let pr = await getProjectRolePayload();

      console.log('save project');
      let projectInsertPayload = {
        'project_name': projectName,
        'project_eng': projectFolder,
        'project_desc': "string",
        'enc_key': enckey,
        'group_id': parseInt(projectGroupId),
        'project_role': pr,
        'issingle': isSingleDataset,
      }
      const url = "/api/project/post_projectSave";
      const payload = projectInsertPayload; // [TODO] need to fill in dynamic data
      console.log('payload', payload);
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
      };

      let promiseResult;
      try {
        promiseResult = await axios.post(url, payload, config);
      }
      catch (error) {
        promiseResult = error.response;
        console.log(url, payload, config);
        console.log("promiseResult/error", promiseResult);
      }
      // const promiseResult = await axiosPlus({ method: "POST", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false, showErrorMsg: true });
      // console.log("API /projects/insert response/error:\n", promiseResult);
      // if (promiseResult.status === 400) {
      //   await setPopUpMsg(promiseResult.data.msg);
      //   await setCheckPopUp(true);
      // }

      // if (!wroteLog["createProject"]) {
      //   await petsLog(session, 0, `Login User ${user.account}建立新專案`, project_name);
      //   setWroteLog(prev => ({ ...prev, ["createProject"]: true }))
      // }
      if (promiseResult.status === 200) {
        // Go back to projects-table
        await router.push('/apps/project/projects-table');
      }

    }
  }


  useEffect(() => {
    // get project member options
    // console.log('change user options');
    // console.log('allUsers', allUsers);
    let optionsTemp = [];
    // if(selectedGroup) {
    allUsers
      .filter((gm) => {
        console.log('selectedGroup', selectedGroup);
        // 單位下啟用且未被停權的人員
        return gm.group_name === selectedGroup.split('_')[1] && gm.ischange && gm.isactive && gm.id !== user.id;
        // return gm.group_name === selectedGroup.split('_')[1];
      })
      .map((pm) => {
        optionsTemp.push({ id: pm.id, label: pm.username + '    ' + pm.email });
      });
    setSelectedUser('');
    setUserOptions(optionsTemp);
    // }
  }, [selectedGroup]);

  useEffect(() => {
    // console.log('ori BasicAutocomplete');
    setUserSelectAutocomplete(
      <BasicAutocomplete
        options={userOptions}
        inputValue={selectedUser}
        setInputValue={setSelectedUser}
        setSelectedId={setSelectedUserId}
        fullWidth
      />
    );
  }, [selectedGroup, userOptions]);

  const columns = useMemo(
    () => [
      {
        Header: '主責單位',
        accessor: 'group_name',
        className: 'cell-center'
      },
      {
        Header: '使用者姓名',
        accessor: 'user_name',
        className: 'cell-center',
        // disableSortBy: true
      },
      {
        Header: '使用者信箱',
        accessor: 'user_email',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '角色',
        accessor: 'user_role',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '刪除',
        className: 'delete',
        disableSortBy: true,
        Cell: ({ row }) => ActionsCell(row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles)
      }
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme, projectMembers, projectRoles]
  );

  const handleGroupSelect = (event) => {
    setSelectedGroup(event.target.value);
  };

  const handleUserRoleSelect = (event) => {
    setSelectedUserRole(event.target.value);
  };

  const handleAddMember = async () => {
    let id = await selectedUserId;
    let name = await selectedUser.split(' ')[0];
    let email = await selectedUser.split(' ')[1];
    let groupId = await selectedGroup.split('_')[0];
    let groupName = await selectedGroup.split('_')[1];
    console.log("selectedUser.split(' ')", selectedUser.split(' '));
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
    await setSelectedUser(null);
  };

  const handleProjectName = (event) => {
    setProjectName(event.target.value);
  };

  const handleProjectFolder = (event) => {
    setProjectFolder(event.target.value);
  };

  const handleEnckey = async () => {
    // Fetch API /projects/list
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      }
    };
    const promiseResult = await axiosPlus({
      method: 'GET',
      stateArray: null,
      url: '/api/project/get_projectGenkey',
      config: config,
      showSuccessMsg: false
    });
    // console.log("promiseResult.data.enc_key:", promiseResult.data.enc_key);

    // Update enckey state
    setEnckey(promiseResult.data.enc_key);
  };

  const handleIsSingleDataset = (event) => {
    //setIsSingleDataset(event.target.value);
    setIsSingleDataset(parseInt(event.target.value));
    console.log("event.target.value", event.target.value);
  };

  return (
    <Page title="new project">
      {/*<MainCard content={false}>*/}
      {/* 頂部進度條 */}
      <Box sx={{ width: '750px', margin: '40px auto 60px auto' }}>
        <Box sx={{ width: '100%', alignItems: 'center' }}>
          <ProjectStepper currentStep={0} terminatedStep={null} />
        </Box>
      </Box>

      <Grid container spacing={6} sx={{ ml: '50px', maxWidth: '1200px' }}>
        <Grid item>
          <Typography variant="h3" sx={{ marginBottom: '20px' }}>
            建立專案及設定
          </Typography>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel>*專案名稱</InputLabel>
          </Grid>
          <Grid item xs={8}>
            <TextField
              fullWidth
              value={projectName}
              onChange={handleProjectName}
              onBlur={async () => {
                await checkProjectName(projectName, config, setCheckPopUp, setPopUpMsg);
              }}
              helperText={'可以是中英數字與底線，不可以加入特殊字元'}
              error={projectName && checkProject(projectName)}
              label={projectName && checkProject(projectName) && '只能包含中英數字與底線'}
            // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
            />
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel>*專案資料夾</InputLabel>
          </Grid>
          <Grid item xs={8}>
            <TextField
              fullWidth
              value={projectFolder}
              onChange={handleProjectFolder}
              onBlur={async () => {
                await checkProjectEng(projectFolder, config, setCheckPopUp, setPopUpMsg);
              }}
              helperText={'可以是英數字與底線，不可以加入特殊字元，也不能是全數字與第一個字為數字開頭'}
              error={projectFolder && checkProjectFolder(projectFolder)}
              label={projectFolder && checkProjectFolder(projectFolder) && '可以是英數字與底線，不可以加入特殊字元，也不能是全數字與第一個字為數字開頭'}
            // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
            />
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel>*金鑰</InputLabel>
          </Grid>
          <Grid item xs={8}>
            <TextField
              fullWidth
              multiline
              label=""
              value={enckey}
              onChange={handleEnckey}
              disabled={true}
              sx={{ '& .Mui-disabled': { backgroundColor: 'disableBGColor' } }}
            />
          </Grid>
          <Grid item lg={2}>
            <Button variant="contained" fullWidth onClick={handleEnckey} sx={{ marginLeft: '20px' }}>
              產生新金鑰
            </Button>
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel>*選擇協作人員</InputLabel>
          </Grid>
          <Grid container item xs={8} spacing={1}>
            <Grid item md={3} xs={3}>
              <Select
                value={selectedGroup}
                // value={selectedGroup ? selectedGroup.split('_')[1] : null}
                displayEmpty
                name="select group name"
                renderValue={(selected) => {
                  if (selected) {
                    return selected.split('_')[1];
                  } else {
                    return null;
                  }
                }}
                fullWidth
                onChange={handleGroupSelect}
              // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
              >
                {allGroups.map((g) => {
                  return <MenuItem value={`${g.id}_${g.group_name}`}>{g.group_name}</MenuItem>;
                })}
              </Select>
            </Grid>
            <Grid item md={6} xs={6}>
              {userSelectAutocomplete}
            </Grid>
            <Grid item md={3} xs={3}>
              <Select
                value={selectedUserRole}
                displayEmpty
                name="select user role"
                renderValue={(selected) => {
                  return selected;
                }}
                fullWidth
                onChange={handleUserRoleSelect}
              // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
              >
                {member_roles.map((mr) => {
                  return <MenuItem value={mr}>{mr}</MenuItem>;
                })}
              </Select>
            </Grid>
          </Grid>
          <Grid item xs={2}>
            <Button variant="outlined" fullWidth onClick={handleAddMember} sx={{ marginLeft: '20px' }}>
              新增
            </Button>
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid xs={2} />
          <Grid xs={8}>
            <MainCard content={false}>
              <ScrollX>
                <ReactTable columns={columns} data={projectMembers} />
              </ScrollX>
            </MainCard>
          </Grid>
        </Grid>

        <Grid container sx={{ margin: '20px 0 0 50px', alignItems: 'center' }}>
          <Grid item xs={2}>
            <InputLabel>*是否為單一資料集</InputLabel>
          </Grid>
          <Grid item xs={8}>
            <FormControl>
              <RadioGroup
                row
                aria-labelledby="demo-row-radio-buttons-group-label"
                name="row-radio-buttons-group"
                value={isSingleDataset}
                //defaultValue={0}
                onChange={handleIsSingleDataset}
              >
                <FormControlLabel value={1} control={<Radio />} label="是" />
                <FormControlLabel value={0} control={<Radio />} label="否" />
              </RadioGroup>
            </FormControl>
          </Grid>
        </Grid>

        <Grid container item>
          <Grid container>
            <Grid item xs={10} />
            <Grid item xs={2}>
              <Button variant="contained" fullWidth onClick={handleSave} sx={{ marginLeft: '20px' }}>
                儲存新增專案
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      {checkPopUp ? (
        <StateControlDialog
          stateArrayOpenControl={[checkPopUp, setCheckPopUp]}
          dialogTitle={popUpMsg}
          dialogContent={null}
          disagreeButtonText={null}
          agreeButtonText="確定"
          agreeButtonOnClick={() => {
            setCheckPopUp(false);
          }}
        />
      ) : (
        <></>
      )}
    </Page>
  );
};

NewProject.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default NewProject;
