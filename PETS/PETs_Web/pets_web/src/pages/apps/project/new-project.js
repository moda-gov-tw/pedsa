import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { styled } from '@mui/material/styles';
import Paper from '@mui/material/Paper';
import { useTheme } from '@mui/material/styles';
import {
  Box,
  Button, Dialog, DialogTitle,
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
  useMediaQuery
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
import {
  HeaderSort,
  IndeterminateCheckbox,
  TableRowSelection
} from 'components/third-party/ReactTable';
import BasicAutocomplete from '../../../sections/components-overview/autocomplete/BasicAutocomplete';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import ProjectStepper from 'sections/apps/progress/project_stepper';
import { checkProject, checkProjecFolder } from "utils/check-rules";

// mock data
import { mockMembers } from "../../../utils/mock-members";
import { mockProjectMembers } from '../../../utils/mock-project-members';
import { mockUserList } from "utils/mock-users";
import { ConfigContext } from "contexts/ConfigContext";
import getALLUsers from "utils/getUsers";
import getALLGroups from "../../../utils/getGroups";
import menuItem from "../../../menu-items";

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
  handleAdd: PropTypes.func,
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
    console.log('newProjectRoles', newProjectRoles);

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
  theme: PropTypes.array,
  projectMembers: PropTypes.object,
  setProjectMembers: PropTypes.func,
  projectRoles: PropTypes.object,
  setProjectRoles: PropTypes.func,
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

  const [projectName, setProjectName] = useState(null);
  const [projectFolder, setProjectFolder] = useState(null);
  const [projectGroupId, setProjectGroupId] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [selectedGroup, setSelectedGroup] = useState(''); //選擇專案成員單位
  const [members, setMembers] = useState(mockMembers);  //所有成員
  const [userOptions, setUserOptions] = useState([]);  //機關下成員選項
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState();
  const [selectedUserRole, setSelectedUserRole] = useState('專案使用者');  //選擇專案成員角色
  const [projectMembers, setProjectMembers] = useState([]);  //專案成員表格資料
  const [projectRoles, setProjectRoles] = useState([]);
  const [enckey, setEnckey] = useState(''); //金鑰
  const [checkPopUp, setCheckPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [userSelectAutocomplete, setUserSelectAutocomplete] = useState(<BasicAutocomplete options={userOptions} inputValue={selectedUser} setInputValue={setSelectedUser} setSelectedId={setSelectedUserId} fullWidth />)

  // 取得專案建立者資訊
  const getUserInfo = async (token) => {
    console.log('getUserInfo');
    await axios.get(`/api/user/get_info/${user.id}`, {
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
        console.log('get user info error', error);
      });
  }

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
      temp.push({ 'member_id': user.id, 'group_id': userInfo.group_id, 'member_role': 3 });
      return temp;
    }
  }

  function handleCheck() {
    if (projectName && projectFolder && enckey && !checkProject(projectName) && !checkProject(projectFolder)) {
      return true;
    } else {
      setCheckPopUp(true);
      setPopUpMsg('請確認專案名稱及專案資料夾皆有填入符合格式規範的內容，且金鑰已生成');
    }
  }

  async function handleClick() {
    // console.log('projectMembers', projectMembers);
    const goNext = await handleCheck();
    if (goNext) {
      let pr = await getProjectRolePayload();
      router.push({
        pathname: '/apps/project/new-project-data-connect',
        // query: { name: '123', age: '456' },// enc_key: enckey,
        query: {
          project_name: projectName, project_eng: projectFolder, enc_key: enckey,
          group_id: projectGroupId,
          project_role: JSON.stringify(pr)
        }
      });
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
      })
    setSelectedUser("");
    setUserOptions(optionsTemp);
    // }
  }, [selectedGroup])

  useEffect(() => {
    // console.log('ori BasicAutocomplete');
    setUserSelectAutocomplete(<BasicAutocomplete options={userOptions} inputValue={selectedUser} setInputValue={setSelectedUser} setSelectedId={setSelectedUserId} fullWidth />)
  }, [selectedGroup, userOptions])

  const columns = useMemo(
    () => [
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
    console.log('selectedUser.split(\' \')', selectedUser.split(' '));
    await setProjectMembers(current =>
      [...current, {
        'group_id': groupId, 'group_name': groupName,
        'member_id': id, 'user_name': name, 'user_email': email,
        'user_role': selectedUserRole, 'user_role_id': member_roles_id_dic[selectedUserRole]
      }]);
    await setProjectRoles(current =>
      [...current, { 'member_id': id, 'group_id': groupId, 'member_role': member_roles_id_dic[selectedUserRole] }]);
    await setSelectedUser(null);
  };

  const handleProjectName = (event) => {
    setProjectName(event.target.value);
  }

  const handleProjectFolder = (event) => {
    setProjectFolder(event.target.value);
  }

  const handleEnckey = async () => {
    // Fetch API /projects/list
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
    };
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

  return (
    <Page title="Customer List">
      {/*<MainCard content={false}>*/}
      {/* 頂部進度條 */}
      <Box sx={{ width: '750px',  margin:"20px auto 60px auto" }} >
        <Box sx={{ width: "100%", alignItems: "center" }} >
          <ProjectStepper currentStep={0} terminatedStep={null} />
        </Box>
      </Box>

      <Grid container spacing={6} sx={{ ml: "50px" }}>
        <Grid container item>
          <Grid item>
            <Stack>
              <Typography variant='h3'>
                建立專案及設定
              </Typography>
              <Divider />
            </Stack>
          </Grid>
        </Grid>

        <Grid container item spacing={3}>
          <Grid container spacing={6} >
            <Grid item lg={2}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案名稱</InputLabel>
            </Grid>
            <Grid item lg={8}>
              <TextField
                fullWidth
                value={projectName}
                onChange={handleProjectName}
                helperText={'可以是中英數字與底線，不可以加入特殊字元'}
                error={checkProject(projectName)}
                label={checkProject(projectName) && '只能包含中英數字與底線'}
              // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
              />
            </Grid>
          </Grid>
        </Grid>

        <Grid container item spacing={3}>
          <Grid container spacing={6} >
            <Grid item lg={2}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案資料夾</InputLabel>
            </Grid>
            <Grid item lg={8}>
              <TextField
                fullWidth
                value={projectFolder}
                onChange={handleProjectFolder}
                helperText={'可以是英數字與底線，不可以加入中文或是特殊字元'}
                error={checkProjecFolder(projectFolder)}
                label={checkProjecFolder(projectFolder) && '只能包含英數字與底線'}
              // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
              />
            </Grid>
          </Grid>
        </Grid>

        <Grid container item spacing={3}>
          <Grid container spacing={6} >
            <Grid item lg={2}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                金鑰
              </InputLabel>
            </Grid>
            <Grid item lg={8}>
              <TextField fullWidth multiline label="" value={enckey} onChange={handleEnckey} disabled={true} sx={{ "& .Mui-disabled": { backgroundColor: "disableBGColor" } }} />
            </Grid>
            <Grid item lg={2}>
              <Button variant="contained" fullWidth onClick={handleEnckey}>產生新金鑰</Button>
            </Grid>
          </Grid>
        </Grid>

        <Grid container item spacing={3}>
          <Grid container spacing={6}>
            <Grid item lg={2}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                選擇協作人員
              </InputLabel>
            </Grid>
            <Grid container item lg={8} spacing={1}>
              <Grid item md={3} lg={3}>
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
                    return <MenuItem value={`${g.id}_${g.group_name}`}>{g.group_name}</MenuItem>
                  })}
                </Select>
              </Grid>
              <Grid item md={6} lg={6}>
                {userSelectAutocomplete}
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
                // sx={{ "& .MuiInputBase-input": { backgroundColor: "inputBGColor" } }}
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
          <Grid container spacing={6}>
            <Grid item lg={10} />
            <Grid item lg={2}>
              <Button
                variant="contained"
                fullWidth
                onClick={handleClick}
              >
                下一步
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      <Dialog open={checkPopUp} onClose={() => { setCheckPopUp(false) }}>
        <DialogTitle>
          {popUpMsg}
        </DialogTitle>
      </Dialog>
    </Page>
  );
};

NewProject.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default NewProject;
