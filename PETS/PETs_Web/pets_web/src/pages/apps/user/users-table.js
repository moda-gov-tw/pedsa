import PropTypes from 'prop-types';
import {useContext, useEffect, useMemo, useState} from 'react';

// next
import { useSession, } from 'next-auth/react';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Menu,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  useMediaQuery
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';

// third-party
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import { PopupTransition } from 'components/@extended/Transitions';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import {
  HeaderSort,
  IndeterminateCheckbox,
  TableRowSelection
} from 'components/third-party/ReactTable';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import AddUser from "sections/apps/user/add-user";
import AlertUserDelete from "sections/apps/user/delete-user";
import AlertUserActivate from "sections/apps/user/activate-user";
import AssignUserProjectAdmin from "sections/apps/user/assign-project-admin";
import petsLog from "sections/apps/logger/insert-system-log";
import getALLUsers from "utils/getUsers";
// import { mockUserList } from 'utils/mock-users';

// assets
import {ConfigContext} from "contexts/ConfigContext";
import axios from "axios";
import useUser from "../../../hooks/useUser";

// ==============================|| REACT TABLE ||============================== //
/**
 * Function: ReactTable
 *
 * Child component of UserListTable
 *
 * @param {{ columns: object, data: object, handleOpenAddDialog: func }} argObject
 * * `columns`: columns in the table.
 * * `data`: data in the table.
 * * `handleOpenAddDialog`: function to control dialog open.
 *
 * @returns {JSX.Element}
 */
function ReactTable({ columns, data, handleOpenAddDialog }) {
  // console.log('ReactTable', data);
  const theme = useTheme();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
  const { userPermission } = useContext(ConfigContext);
  const sortBy = { id: 'fatherName', desc: false };

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
    state: { selectedRowIds },
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
        <Stack
          direction={matchDownSM ? 'column' : 'row'}
          spacing={1}
          justifyContent="space-between"
          alignItems="center"
          sx={{ p: 3, pb: 0 }}
        >
          {userPermission.includes('super_admin') && (
              <Stack direction={matchDownSM ? 'column' : 'row'} alignItems="center" spacing={1}>
                  <Button sx={{ bgcolor: "#226cea", minWidth: '100px' }} variant="contained" startIcon={<AddIcon />} onClick={handleOpenAddDialog} size="small">
                      新增人員
                  </Button>
              </Stack>
          )}
        </Stack>
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
  handleOpenAddDialog: PropTypes.func,
};

// 顯示使用者角色，檢查is_super_admin、is_group_admin、is_project_admin欄位
const handleRoles = (row) => {
    let userRoles = '';
    if(row.original.is_super_admin) {
        userRoles = userRoles + '系統管理員';
    }
    if(row.original.is_group_admin) {
        if(userRoles !== ''){
            userRoles = userRoles + ', 單位管理員';
        }else {
            userRoles = userRoles + '單位管理員';
        }
    }
    if(row.original.is_project_admin.status) {
        if(userRoles !== ''){
            userRoles = userRoles + ', 專案管理員';
        } else {
            userRoles = userRoles + '專案管理員';
        }
    }
    return userRoles;
}

// 顯示使用者狀態，檢查ischange、isactive欄位
const handleStatus = (row) => {
    let viewValue = "啟用"
    if(!row.original.ischange) {
        viewValue = "未啟用";
    }
    if(!row.original.isactive) {
        viewValue = "停權";
    }
    return viewValue;
};

const ActionsCell = (row, setUser, setUserId, setUserAdminRoles, setUserIsActive, setUserIsProjectAdmin, setUserProjectAdminId, handleOpenAddDialog, handleDeleteDialog, handleActivateDialog, handleAssignProjectAdminDialog) => {
  const { data: session } = useSession();
  const loginUser = useUser();
  const { userPermission } = useContext(ConfigContext);

  const [openMoreMenu, setOpenMoreMenu] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [popUp, setPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  const doPasswordReset = async() => {
      await axios.put('/api/user/put_admin_uppwd',
          {
                    'member_id': row.original.id
               },
          {
                    headers: {
                    Authorization: `Bearer ${session.tocken.loginUserToken}`
                }})
          .then(async (res) => {
              await setPopUpMsg(`修改密碼成功，預設密碼為:${res.data.obj.new_password}`);
              if (!wroteLog["resetPassword"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account}修改 ${row.original.useraccount} 密碼成功`);
                  setWroteLog(prev => ({ ...prev, ["resetPassword"]: true }))
              }
              await setPopUp(true);
          })
          .catch(async (err) => {
              await setPopUpMsg(`修改${row.original.useraccount}密碼失敗，${err.msg}`);
              if (!wroteLog["resetPassword"]) {
                  await petsLog(session, 0, `Login User ${loginUser.account}修改 ${row.original.useraccount} 密碼失敗`);
                  setWroteLog(prev => ({ ...prev, ["resetPassword"]: true }))
              }
              await setPopUp(true);
          })
  }

  const handlePasswordReset = async() => {
      await setPopUpMsg(`修改密碼將自動產生一組新密碼，舊密碼將立即失效，且使用者需重新啟用帳號。確定要修改密碼嗎?`);
      await setPopUp(true);
  }

  const handleEdit = async() => {
      console.log('edit user');
      await handleOpenAddDialog();
      console.log('user id', row.original.id, row.values);
      setOpenMoreMenu(false);
  }

  const handleDelete = () => {
      handleDeleteDialog();
      setOpenMoreMenu(false);
  }

  const handleActivate = () => {
      handleActivateDialog();
      setOpenMoreMenu(false);
  }

  const handleAssignUserProjectAdmin = () => {
      handleAssignProjectAdminDialog();
      setOpenMoreMenu(false);
  }

  const handleClose = () => {
      setOpenMoreMenu(false);
  }

  return (
    <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
      <Tooltip title="more">
        <IconButton
            onClick={async (e) => {
                setAnchorEl(e.currentTarget);
                e.stopPropagation();
                setOpenMoreMenu(true);
                console.log('row.values', row.values);
                setUser(row.values);
                setUserId(row.original.id);
                setUserAdminRoles(handleRoles(row).split(', '))
                setUserIsActive(row.original.isactive);
                setUserIsProjectAdmin(row.original.is_project_admin.status);
                if(row.original.is_project_admin.status) {
                    setUserProjectAdminId(row.original.is_project_admin.id);
                }
            }}
        >
            <MoreHorizIcon />
        </IconButton>
      </Tooltip>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={openMoreMenu}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'basic-button',
        }}
      >
        {userPermission.includes('super_admin') ? (
            (row.original.ischange ? (
                <>
                    <MenuItem onClick={handleEdit}>編輯</MenuItem>
                    <MenuItem onClick={handlePasswordReset}>修改密碼</MenuItem>
                    <MenuItem onClick={handleActivate}>停權/復權</MenuItem>
                    <MenuItem onClick={handleDelete}>刪除</MenuItem>
                </>
            ) : (
                <>
                    <MenuItem onClick={handlePasswordReset}>修改密碼</MenuItem>
                    <MenuItem onClick={handleDelete}>刪除</MenuItem>
                </>
            ))
        ) : (
            <>
                <MenuItem onClick={handleAssignUserProjectAdmin}>移除/設為專案管理員</MenuItem>
            </>
        )}
      </Menu>
      <Dialog open={popUp} onClose={() => {setPopUp(false)}}>
          <DialogTitle>{'修改密碼'}</DialogTitle>
          <DialogContent>
              <DialogContentText id="alert-dialog-description">
                  {popUpMsg}
              </DialogContentText>
          </DialogContent>
          {(popUpMsg && popUpMsg.includes('修改密碼成功')) ? (
              <DialogActions>
                  <Button onClick={() => {setPopUp(false)}} autoFocus>
                    確定
                  </Button>
              </DialogActions>
          ) : (
              <DialogActions>
                  <Button onClick={() => {setPopUp(false)}}>取消</Button>
                  <Button onClick={doPasswordReset} autoFocus>
                    確定
                  </Button>
              </DialogActions>
          )}
      </Dialog>
    </Stack>
  );
};

ActionsCell.propTypes = {
  row: PropTypes.object,
  setUser: PropTypes.func,
  setUserId: PropTypes.func,
  setUserAdminRoles: PropTypes.func,
  setUserIsActive: PropTypes.func,
  setUserIsProjectAdmin: PropTypes.func,
  setUserProjectAdminId: PropTypes.func,
  handleOpenAddDialog: PropTypes.func,
  handleDeleteDialog: PropTypes.func,
  handleActivateDialog: PropTypes.func,
};

// Section Cell and Header
const SelectionHeader = ({ getToggleAllPageRowsSelectedProps }) => (
  <IndeterminateCheckbox indeterminate {...getToggleAllPageRowsSelectedProps()} />
);

SelectionHeader.propTypes = {
  getToggleAllPageRowsSelectedProps: PropTypes.func
};

/**
 * Function: UserListTable
 *
 * Child component of UserListTable
 *
 * @returns {JSX.Element}
 */
const UserListTable = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const loginUser = useUser();
  const { allUsers, setAllUsers, userPermission } = useContext(ConfigContext); // 所有人員及登入人員權限
  const [openAddDialog, setOpenAddDialog] = useState(false);  // 是否跳出新增/編輯人員彈出視窗
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);  // 是否跳出提示刪除人員彈出視窗
  const [openActivateDialog, setOpenActivateDialog] = useState(false);  // 是否跳出提示停權/復權人員彈出視窗
  const [openAssignProjectAdmin, setOpenAssignProjectAdmin] = useState(false);   // 是否跳出提示新增/移除人員為專案管理員彈出視窗
  const [user, setUser] = useState(null); // 列表裡面選擇的某一人員
  const [userId, setUserId] = useState(null); // 列表裡面選擇的某一人員ID
  const [userInfo, setUserInfo] = useState(null);
  const [userAdminRoles, setUserAdminRoles] = useState([]);
  const [userIsActive, setUserIsActive] = useState(null); // 列表裡面選擇的某一人員isactive狀態
  const [userIsProjectAdmin, setUserIsProjectAdmin] = useState(null); // 列表裡面選擇的某一人員is_project_admin狀態
  const [userProjectAdminId, setUserProjectAdminId] = useState(null); // 列表裡面選擇的某一人員project admin的role_id
  const [wroteLog, setWroteLog] = useState({});

  const handleOpenAddDialog = () => {
    // 開啟新增/編輯彈出視窗
    console.log('開啟新增/編輯彈出視窗');
    setOpenAddDialog(true);
  };

  const handleCloseAddDialog = () => {
      // 關閉新增/編輯彈出視窗
      setOpenAddDialog(false);
      if(user){
          console.log('close edit dialog and set the user to null');
          setUser(null);
      }
  }

  const handleDeleteDialog = () => {
      // 是否開啟刪除提示彈出視窗
      setOpenDeleteDialog(!openDeleteDialog);
      if(user){
          console.log('close delete dialog and set the user to null');
          setUser(null);
      }
  }

  const handleActivateDialog = () => {
      // 是否開啟停權/復權提示彈出視窗
      setOpenActivateDialog(!openActivateDialog);
      if(user){
          console.log('close activate dialog and set the user to null');
          setUser(null);
      }
  }

  const handleAssignProjectAdminDialog = () => {
      setOpenAssignProjectAdmin(!openAssignProjectAdmin);
      if(user){
          console.log('close assugn project admin dialog and set the user to null');
          setUser(null);
      }
  }

  // 取得登入使用者資訊
  const getUserInfo = async (token) => {
    console.log('getUserInfo');
    await axios.get(`/api/user/get_info/${loginUser.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
        .then((response) => {
            console.log('get user info', response.data.obj);
            setUserInfo(response.data.obj);
        })
        .catch((error) => {
          console.log('get user info error', error);
        });
  };

  useEffect(() => {
      // 取得所有人員
      getALLUsers(setAllUsers, session.tocken.loginUserToken);
      getUserInfo(session.tocken.loginUserToken);
      if (!wroteLog["enterPage"]) {
          petsLog(session, 0, `Login User ${loginUser.account} 進入人員列表`);
          setWroteLog(prev => ({ ...prev, ["enterPage"]: true }))
      }
  }, []);

  const columns = useMemo(() => {
      let columns = [
      {
        Header: '姓名',
        accessor: 'username',
        className: 'cell-center'
      },
      {
        Header: '帳號名稱',
        accessor: 'useraccount',
        className: 'cell-center'
      },
      {
        Header: 'E-mail',
        accessor: 'email',
        className: 'cell-center',
      },
      {
        Header: '機關',
        accessor: 'group_name',
        className: 'cell-center',
        disableSortBy: true,
      },
      {
        Header: '角色',
        className: 'cell-center',
        disableSortBy: true,
        Cell: ({ row }) => handleRoles(row)
      },
      {
        Header: '狀態',
        className: 'cell-center',
        disableSortBy: true,
        Cell: ({ row }) => handleStatus(row)
      }
      ];
      if(userPermission.includes('super_admin') || userPermission.includes('group_admin')){
          columns.push(
              {
                Header: '其他',
                className: 'download',
                disableSortBy: true,
                Cell: ({ row }) => ActionsCell(row, setUser, setUserId, setUserAdminRoles, setUserIsActive, setUserIsProjectAdmin, setUserProjectAdminId, handleOpenAddDialog, handleDeleteDialog, handleActivateDialog, handleAssignProjectAdminDialog)
              }
          )
      }
      return columns;
  }, [userPermission]);

  // const columns = useMemo(
  //   () => [
  //     {
  //       Header: '姓名',
  //       accessor: 'username',
  //       className: 'cell-center'
  //     },
  //     {
  //       Header: '帳號名稱',
  //       accessor: 'useraccount',
  //       className: 'cell-center'
  //     },
  //     {
  //       Header: 'E-mail',
  //       accessor: 'email',
  //       className: 'cell-center',
  //     },
  //     {
  //       Header: '機關',
  //       accessor: 'group_name',
  //       className: 'cell-center',
  //       disableSortBy: true,
  //     },
  //     {
  //       Header: '角色',
  //       className: 'cell-center',
  //       disableSortBy: true,
  //       Cell: ({ row }) => handleRoles(row)
  //     },
  //     {
  //       Header: '狀態',
  //       className: 'cell-center',
  //       disableSortBy: true,
  //       Cell: ({ row }) => handleStatus(row)
  //     },
  //     {
  //       Header: '其他',
  //       className: 'download',
  //       disableSortBy: true,
  //       Cell: ({ row }) => ActionsCell(row, setUser, setUserId, setUserAdminRoles, setUserIsActive, handleOpenAddDialog, handleDeleteDialog, handleActivateDialog)
  //     }
  //   ],
  //   // eslint-disable-next-line react-hooks/exhaustive-deps
  //   [theme]
  // );

  return (
    <Page title="Customer List">
      {userInfo && (
          (!userPermission.includes('super_admin')) ? (
              <>
                  <MainCard content={false}>
                    <ScrollX>
                      <ReactTable columns={columns} data={allUsers.filter((u) => u.group_id===userInfo.group_id)} handleOpenAddDialog={handleOpenAddDialog}/>
                    </ScrollX>
                  </MainCard>
                  {/*新增/移除人員為專案管理員*/}
                  <AssignUserProjectAdmin user={user} userId={userId} userIsProjectAdmin={userIsProjectAdmin} userProjectAdminId={userProjectAdminId} allUsers={allUsers} setAllUsers={setAllUsers} open={openAssignProjectAdmin} handleClose={handleAssignProjectAdminDialog} />
              </>
          ) : (
              <>
                  <MainCard content={false}>
                    <ScrollX>
                      <ReactTable columns={columns} data={allUsers} handleOpenAddDialog={handleOpenAddDialog}/>
                    </ScrollX>
                  </MainCard>
                  <Dialog
                    maxWidth="sm"
                    fullWidth
                    TransitionComponent={PopupTransition}
                    onClose={handleCloseAddDialog}
                    open={openAddDialog}
                    sx={{ '& .MuiDialog-paper': { p: 0 } }}
                  >
                    {/*新增/編輯人員*/}
                    <AddUser user={user} userId={userId} userAdminRoles={userAdminRoles} allUsers={allUsers} setAllUsers={setAllUsers} onCancel={handleCloseAddDialog} />
                  </Dialog>
                  {/*刪除人員*/}
                  <AlertUserDelete user={user} userId={userId} allUsers={allUsers} setAllUsers={setAllUsers} open={openDeleteDialog} handleClose={handleDeleteDialog} />
                  {/*停權/復權人員*/}
                  <AlertUserActivate user={user} userId={userId} userIsActive={userIsActive} allUsers={allUsers} setAllUsers={setAllUsers} open={openActivateDialog} handleClose={handleActivateDialog} />
              </>
          )
      )}
    </Page>
  );
};

UserListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default UserListTable;
