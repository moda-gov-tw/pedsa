import PropTypes from 'prop-types';
import {useContext, useEffect, useMemo, useState} from 'react';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Button,
  Dialog,
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
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

// project import
import {ConfigContext} from "contexts/ConfigContext";
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
import AddGroup from 'sections/apps/group/add-group';
import AlertGroupDelete from 'sections/apps/group/delete-group';
import getALLGroups from 'utils/getGroups';
import useUser from "hooks/useUser";
import { mockGroupList } from 'utils/mock-groups';
import petsLog from "sections/apps/logger/insert-system-log";

// assets


// ==============================|| REACT TABLE ||============================== //
/**
 * Function: ReactTable
 *
 * Child component of GroupListTable
 *
 * @param {{ columns: object, data: object, handleOpenAddDialog: func }} argObject
 * * `columns`: columns in the table.
 * * `data`: data in the table.
 * * `handleOpenAddDialog`: function to control dialog open/close.
 *
 * @returns {JSX.Element}
 */
function ReactTable({ columns, data, handleOpenAddDialog }) {
  // console.log('ReactTable', data);
  const theme = useTheme();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
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
          <Stack direction={matchDownSM ? 'column' : 'row'} alignItems="center" spacing={1}>
              <Button sx={{ bgcolor: "#226cea", minWidth: '100px' }} variant="contained" startIcon={<AddIcon />} onClick={handleOpenAddDialog} size="small">
                  新增單位
              </Button>
          </Stack>
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

const ActionsCell = (row, setGroup, setGroupId, handleOpenAddDialog, handleDeleteDialog) => {
  const { data: session } = useSession();

  const [openMoreMenu, setOpenMoreMenu] = useState(false); // 打開...選單
  const [anchorEl, setAnchorEl] = useState(null); // 選單位置

  const handleEdit = () => {
      // console.log('edit group');
      handleOpenAddDialog();
      // console.log('group id', row.original.id, row.values);
      setOpenMoreMenu(false);
  }

  const handleDelete = () => {
      handleDeleteDialog();
      setOpenMoreMenu(false);
  }

  return (
    <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
      <Tooltip title="more">
        <IconButton
            onClick={(e) => {
                e.stopPropagation();
                setOpenMoreMenu(true);
                setGroup(row.values);
                setGroupId(row.original.id);
                setAnchorEl(e.currentTarget);
            }}
        >
            <MoreHorizIcon />
        </IconButton>
      </Tooltip>
      <Menu
        id="basic-menu"
        anchorEl={anchorEl}
        open={openMoreMenu}
        onClose={() => {setOpenMoreMenu(false)}}
        MenuListProps={{
          'aria-labelledby': 'basic-button',
        }}
      >
        <MenuItem onClick={handleEdit}>編輯</MenuItem>
        <MenuItem onClick={handleDelete}>刪除</MenuItem>
      </Menu>
    </Stack>
  );
};

ActionsCell.propTypes = {
  row: PropTypes.object,
  setGroup: PropTypes.func,
  setGroupId: PropTypes.func,
  handleOpenAddDialog: PropTypes.func,
  handleDeleteDialog: PropTypes.func
};

// Section Cell and Header
const SelectionHeader = ({ getToggleAllPageRowsSelectedProps }) => (
  <IndeterminateCheckbox indeterminate {...getToggleAllPageRowsSelectedProps()} />
);

SelectionHeader.propTypes = {
  getToggleAllPageRowsSelectedProps: PropTypes.func
};


/**
 * Function: GroupListTable
 *
 * @returns {JSX.Element}
 */
const GroupListTable = () => {
  const theme = useTheme();
  const { data: session } = useSession();
  const user = useUser();

  // const [allGroups, setAllGroups] = useState([]);
  const { allGroups, setAllGroups, userPermission } = useContext(ConfigContext); // 所有單位
  const [openAddDialog, setOpenAddDialog] = useState(false);  // 是否跳出新增/編輯單位彈出視窗
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);  // 是否跳出提示刪除單位彈出視窗
  const [group, setGroup] = useState(null); // 列表裡面選擇的某一單位
  const [groupId, setGroupId] = useState(null); // 列表裡面選擇的某一單位ID
  const [userInfo, setUserInfo] = useState(null);
  const [theGroup, setTheGroup] = useState(null);

  const handleOpenAddDialog = () => {
    // 是否開啟編輯彈出視窗
    setOpenAddDialog(true);
  };

  const handleCloseAddDialog = () => {
      // 關閉新增/編輯彈出視窗
      setOpenAddDialog(false);
      if(group){
          console.log('close edit dialog and set the group to null');
          setGroup(null);
      }
  }

  const handleDeleteDialog = () => {
      // 是否開啟刪除提示彈出視窗
      setOpenDeleteDialog(!openDeleteDialog);
      if(group){
          console.log('close edit dialog and set the group to null');
          setGroup(null);
      }
  }

  useEffect(() => {
      // 取得所有機關
      if(userPermission.includes('super_admin')) {
          getALLGroups(setAllGroups, session.tocken.loginUserToken);
          petsLog(session, 0, `Login User ${user.account}進入單位列表`);
      }else{
          getUserGroupInfo(session.tocken.loginUserToken);
          petsLog(session, 0, `Login User ${user.account}進入單位列表`);
      }
  }, [userPermission]);

  // 取得登入使用者單位資訊(for group admin)
  const getUserGroupInfo = async (token) => {
    console.log('getUserGroupInfo');
    await axios.get(`/api/user/get_info/${user.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
        .then(async (response) => {
            console.log('get user info', response.data.obj);
            await axios.get(`/api/group/get_info/${response.data.obj.group_id}`, {
              headers: {
                Authorization: `Bearer ${token}`
              }
            })
                .then((response) => {
                    console.log('get group info', response.data.obj);
                    setTheGroup(response.data.obj);
                })
                .catch((error) => {
                  console.log('get group info error', error);
                });
        })
        .catch((error) => {
          console.log('get user info error', error);
        });
  };

  // console.log('userPermission', userPermission);

  // 列表欄位
  const columns = useMemo(
    () => {
        let columns = [
          {
            Header: '單位名',
            accessor: 'group_name',
            className: 'cell-center'
          },
          {
            Header: '單位代號',
            accessor: 'group_type',
            className: 'cell-center',
          },
          {
            Header: '專案總數',
            accessor: 'project_quota',
            className: 'cell-center',
            disableSortBy: true,
          },
          {
            Header: '單位管理員帳號',
            accessor: 'owner_email',
            className: 'cell-center',
            disableSortBy: true,
          },
          {
            Header: '單位管理員姓名',
            accessor: 'owner_username',
            className: 'cell-center',
            disableSortBy: true,
          },
          {
            Header: '其他',
            className: 'download',
            disableSortBy: true,
            Cell: ({ row }) => ActionsCell(row, setGroup, setGroupId, handleOpenAddDialog, handleDeleteDialog)
          }
        ]
        // if(userPermission.includes('super_admin')){
        //     columns.push(
        //         {
        //             Header: '其他',
        //             className: 'download',
        //             disableSortBy: true,
        //             Cell: ({ row }) => ActionsCell(row, setGroup, setGroupId, handleOpenAddDialog, handleDeleteDialog)
        //         })
        // }
        return columns;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [userPermission]
  );

  return (
    <Page title="Customer List">
      {theGroup && (
          userPermission.includes('group_admin') && (
              <MainCard content={false}>
                {/*單位列表表格*/}
                <ScrollX>
                  <ReactTable columns={columns} data={[theGroup]} handleOpenAddDialog={handleOpenAddDialog}/>
                </ScrollX>
              </MainCard>
          )
      )}
      {userPermission.includes('super_admin') && (
          <MainCard content={false}>
            {/*單位列表表格*/}
            <ScrollX>
              <ReactTable columns={columns} data={allGroups} handleOpenAddDialog={handleOpenAddDialog}/>
            </ScrollX>
          </MainCard>
      )}
      {/*新增/編輯單位的彈出視窗*/}
      <Dialog
        maxWidth="sm"
        fullWidth
        TransitionComponent={PopupTransition}
        onClose={handleCloseAddDialog}
        open={openAddDialog}
        sx={{ '& .MuiDialog-paper': { p: 0 }, transition: 'transform 225ms' }}
      >
        {/*新增/編輯單位*/}
        <AddGroup group={group} groupId={groupId} allGroups={allGroups} setAllGroups={setAllGroups} onCancel={handleCloseAddDialog} />
      </Dialog>
      {/*刪除單位*/}
      <AlertGroupDelete group={group} groupId={groupId} allGroups={allGroups} setAllGroups={setAllGroups} open={openDeleteDialog} handleClose={handleDeleteDialog} />
    </Page>
  );
};

GroupListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default GroupListTable;
