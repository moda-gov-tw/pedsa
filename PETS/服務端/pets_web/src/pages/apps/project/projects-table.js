import useClock from 'hooks/useClock';
import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import AddIcon from '@mui/icons-material/Add';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import {
  Button,
  Dialog,
  IconButton,
  Menu,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  Tooltip,
  Typography,
  useMediaQuery
} from '@mui/material';
import { useTheme } from '@mui/material/styles';

// third-party
import axios from 'axios';
import { useExpanded, useFilters, useGlobalFilter, usePagination, useRowSelect, useSortBy, useTable } from 'react-table';
// import { saveAs } from 'file-saver';

// project import
import { PopupTransition } from 'components/@extended/Transitions';
import MainCard from 'components/MainCard';
import Page from 'components/Page';
import { HeaderSort, IndeterminateCheckbox, TableRowSelection } from 'components/third-party/ReactTable';
import { ConfigContext } from 'contexts/ConfigContext';
import { roles_id_member_dic } from 'data/member-role';
import useUser from 'hooks/useUser';
import Layout from 'layout';
import StateControlDialog from 'sections/apps/Dialog/state-dialog';
import petsLog from 'sections/apps/logger/insert-system-log';
import EditProjectMember from 'sections/apps/member/edit-project-member';
import BasicAutocomplete from 'sections/components-overview/autocomplete/BasicAutocomplete';
import { GlobalFilter, renderFilterTypes } from 'utils/react-table';

// ==============================|| API ||============================== //

// API: fetch project list
const handleFetchProjectList = (session, [projectList, setProjectList]) => {
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  axiosPlus({
    method: 'GET',
    stateArray: [projectList, setProjectList],
    url: '/api/project/get_projectList',
    config: config,
    showSuccessMsg: false
  }).then((response) => {
    if (!response.status) {
      // console.log('GET projectList fail', response);
      console.log('GET projectList fail');
    }
  });
};

/**
 * handleGetProjectDetail
 * API: fetch project detail
 * @param {any} session
 * @param {String} project_id
 * @param {Array} returnColumnFilterList
 * String of array. 填入 projectDetail 的 key，可使 return object 只包含 returnColumnFilterList 所過濾的的資料
 * @param {any} setProjectDetail
 * Hook state. 將過濾結果存入 state
 * @returns {Object} Object of filterd projectDetail
 */
const handleGetProjectDetail = async (session, project_id, returnColumnFilterList = [], setProjectDetail = null) => {
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
  if (setProjectDetail) setProjectDetail(returnObject);
  return returnObject;
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
    // console.log('PUT projectStatus success');
  } else console.log('PUT projectStatus fail', promiseResult);
};

// API: delete project
const handleProjectDelete = async (session, project_id) => {
  // Get current project_id
  // console.log(`Delete project_id = ${project_id}`);
  // API /projects/delete
  const url = '/api/project/post_projectDelete';
  const payload = { project_id: project_id };
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    }
  };
  const promiseResult = await axiosPlus({
    method: 'POST',
    stateArray: null,
    url: url,
    payload: payload,
    config: config,
    showSuccessMsg: false
  });
  if (promiseResult.status == 200 && promiseResult.data.status == true) {
    console.log('POST projectDelete success');
  } else console.log('POST projectDelete fail', promiseResult);

  return promiseResult;
};

// API: reset project status to 1
const handleProjectReset = async (session, project_id) => {
  // Current project_id
  // console.log(`Reset project_id = ${project_id}`);
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
      // console.log(`子系統_${whom} 專案名稱 ${project_eng} 不存在 (或是專案正在建立中):`, promiseResult);
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

// ==============================|| tableRow Button Routering ||============================== //

const tableRowButtonStatus2URL = {
  0: ['/apps/project/new-project-data-connect', '/apps/project/project-data-connect'],
  1: '/apps/project/edit-project',
  2: '/apps/project/data-check',
  3: '',
  4: '/apps/project/privacy-enhancement',
  5: '/apps/project/privacy-enhancement',
  6: '/apps/project/privacy-enhancement',
  7: '/apps/project/privacy-enhancement',
  8: '/apps/project/privacy-enhancement',
  9: '/apps/project/privacy-enhancement',
  90: '/apps/project/edit-project', // 安全資料鏈結錯誤 -> 可進入編輯專案頁面
  91: '/apps/project/privacy-enhancement', // 可用性分析錯誤 -> 可進入原頁面 (目前只有隱私強化頁面可進去)
  92: '/apps/project/edit-project' // join 之後，資料匯入失敗
};

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
  // console.log('ReactTable', data);
  const { data: session } = useSession();
  const theme = useTheme();
  const router = useRouter();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
  const { userPermission } = useContext(ConfigContext);
  const sortBy = { id: 'fatherName', desc: false };

  const [projNum, setProjNum] = useState(null);
  const [popUp, setPopUp] = useState(false);

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  const handleChangePage = (event, newPage) => {
    // For TablePagination
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    // For TablePagination
    setRowsPerPage(event.target.value);
    setPage(0);
  };

  function customLabelDisplayedRows({ from, to, count }) {
    // For TablePagination
    return `第${from}–${to}筆 ${count !== -1 ? `共${count}筆` : `超過${to}筆`}`;
  }

  async function getProjNum() {
    const url = '/api/project/get_checkGroupProjNum';
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      }
    };
    const promiseResult = await axios.get(url, config);
    setProjNum(promiseResult.data.obj);
  }

  useEffect(() => {
    getProjNum();
  }, []);

  async function handleAdd() {
    if (projNum.gp_project_num < projNum.gp_project_quota_limit) {
      await router.push('/apps/project/new-project');
    } else {
      setPopUp(true);
    }
  }

  // 控制點選列按鈕的權限
  const handleTableRowButtonPermission = (userProjectRole) => {
    // super admin不受project role限制
    if (userPermission.includes('super_admin')) {
      return true;
    } else if (userPermission.length === 1 && userPermission[0] === 'group_admin') {
      return false;
    } else if (userPermission.some((p) => ['group_admin', 'project_admin'].includes(p))) {
      //group_admin 和 project_admin視專案角色決定more選單選項
      if (userProjectRole !== 5) {
        // project admin, project user
        return true;
      } else {
        // data provider
        return false;
      }
    } else {
      switch (userProjectRole) {
        case 5:
          // console.log(`Project data provider, project role is:`, userProjectRole);
          return false;
        case 4:
          // console.log(`Project user, project role is:`, userProjectRole);
          return true;
        case 3:
          // console.log(`project admin, project role is:`, userProjectRole);
          return true;
        case 2:
          // console.log(`Group admin, project role is:`, userProjectRole);
          return false;
        case 1:
          // console.log(`Super admin, project role is:`, userProjectRole);
          return true;
        default:
          return false;
      }
    }
  };

  // 列按鈕的點擊事件
  async function handleReactTableOnClick(event, cell, props) {
    // console.log(cell.column);
    if (cell.column.Header != '更多') {
      router.push({
        pathname: props.clickURL,
        query: {
          project_id: props.projectID,
          project_name: props.projectName,
          project_group_id: props.projectGroupID,
          project_status: props.projectStatus,
          isSingleDataset: props.isSingleDataset
        }
      });
    } else return;
  }

  // 列按鈕的 Child-component: 專案流程按鈕 (Enabled)
  const ButtonTableRowEnabled = ({ row, row_index, onClickProps }) => (
    <TableRow key={row_index} {...row.getRowProps()} style={{ cursor: 'pointer' }}>
      {row.cells.map((cell, index) => {
        const isProcessing = ["安全資料鏈結處理中", "可用性分析處理中", "隱私安全服務強化處理"].includes(cell.value);
        const style = {
          color: isProcessing ? 'blue' : '',
          fontWeight: isProcessing ? 'bold' : '',
        };

        return (
          <TableCell
            key={index}
            {...cell.getCellProps([{ className: cell.column.className }])}
            onClick={(event) => {
              handleReactTableOnClick(event, cell, onClickProps);
            }}
            style={style}
          >
            {cell.render('Cell')}
          </TableCell>
        );
      })}
    </TableRow>
  );

  // 列按鈕的 Child-component: 專案流程按鈕 (Disabled)
  const ButtonTableRowDisabled = ({ row, row_index }) => (
    <TableRow key={row_index} {...row.getRowProps()} sx={{ backgroundColor: 'disableBGColor' }}>
      {row.cells.map((cell, index) => {
        const isProcessing = ["安全資料鏈結處理中", "可用性分析處理中", "隱私安全服務強化處理"].includes(cell.value);
        const style = {
          color: isProcessing ? 'red' : '',
          fontWeight: isProcessing ? 'bold' : '',
        };
      return(
        <TableCell key={index} {...cell.getCellProps([{ className: cell.column.className }])} style={style} /*style={{ cursor: 'not-allowed' }}*/>
          {cell.render('Cell')}
        </TableCell>
      )}
      )}
    </TableRow>
  );

  // 列按鈕的 Child-component: 專案流程按鈕 (檢視專案)
  const ButtonTableRowViewProject = ({ row, row_index, onClickProps }) => (
    <TableRow key={row_index} {...row.getRowProps()} style={{ cursor: 'pointer' }}>
      {row.cells.map((cell, index) => (
        <TableCell
          key={index}
          {...cell.getCellProps([{ className: cell.column.className }])}
          onClick={(event) => {
            handleReactTableOnClick(event, cell, onClickProps);
          }}
        >
          {cell.render('Cell')}
        </TableCell>
      ))}
    </TableRow>
  );

  // Component: 列按鈕
  const ButtonTableRow = ({ row, row_index }) => {
    const projectStatus = row.cells[0].row.original.project_status;
    const projectID = row.cells[0].row.original.project_id;
    const projectName = row.cells[0].row.original.project_name;
    const projectGroupID = row.cells[0].row.original.project_group_id;
    const userProjectRole = row.cells[0].row.original.project_role;
    const isSingleDataset = row.cells[0].row.original.issingle;

    if (handleTableRowButtonPermission(userProjectRole)) {
      let clickURL;
      if (projectStatus == 0) {
        clickURL = tableRowButtonStatus2URL[projectStatus][isSingleDataset];
      } else {
        clickURL = tableRowButtonStatus2URL[projectStatus];
      }
      // const clickURL = tableRowButtonStatus2URL[projectStatus];

      if (clickURL != '') {
        // Enable
        const onClickProps = { projectID, projectName, projectGroupID, clickURL, projectStatus, isSingleDataset };
        const _props = { row, row_index, onClickProps };
        return <ButtonTableRowEnabled {..._props} />;
      } else {
        // Disabled
        const _props = { row, row_index };
        return <ButtonTableRowDisabled {..._props} />;
      }
    } else {
      // For group admin，不能執行專案流程
      const onClickProps = { projectID, projectName, projectGroupID, clickURL: '/apps/project/view-project' };
      const _props = { row, row_index, onClickProps };
      return <ButtonTableRowViewProject {..._props} />;
    }
  };

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
        <Stack
          direction={matchDownSM ? 'column' : 'row'}
          spacing={1}
          justifyContent="space-between"
          alignItems="center"
          sx={{ p: 3, pb: 0 }}
        >
          <GlobalFilter
            preGlobalFilteredRows={preGlobalFilteredRows}
            globalFilter={globalFilter}
            setGlobalFilter={setGlobalFilter}
            size="small"
          />
          <Stack direction={matchDownSM ? 'column' : 'row'} alignItems="center" spacing={1}>
            {userPermission.includes('group_admin') && projNum && (
              <Typography gutterBottom sx={{ fontSize: '14px', paddingRight: '20px', color: '#226cea' }}>
                {`專案限制總量:  ${projNum.gp_project_quota_limit}，目前專案數量: ${projNum.gp_project_num}  `}
              </Typography>
            )}
            {userPermission.length > 0 && (
              <Button
                sx={{ bgcolor: '#226cea', minWidth: '100px' }}
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAdd}
                size="small"
              >
                建立專案
              </Button>
            )}
          </Stack>
        </Stack>
        <TableContainer /* sx={{ maxHeight: '100px' }} */>
          <Table {...getTableProps()}>
            <TableHead>
              {headerGroups.map((headerGroup, index) => (
                <TableRow {...headerGroup.getHeaderGroupProps()} key={index} sx={{ '& > th:first-of-type': { width: '250px' } }}>
                  {headerGroup.headers.map((column, i) => (
                    <TableCell key={i} {...column.getHeaderProps([{ className: column.className }])}>
                      <HeaderSort column={column} sort />
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableHead>
            <TableBody {...getTableBodyProps()}>
              {rows.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row, index) => {
                prepareRow(row);
                return <ButtonTableRow row={row} row_index={index} />;
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Stack>
      <TablePagination
        sx={{ '.MuiTablePagination-toolbar': { width: '70%' /* , backgroundColor: '#226cea' */ } }}
        labelRowsPerPage="每頁顯示筆數"
        rowsPerPageOptions={[10, 20, 50, 100]}
        labelDisplayedRows={customLabelDisplayedRows}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        showFirstButton
        showLastButton
      />
      {popUp && (
        <StateControlDialog
          stateArrayOpenControl={[popUp, setPopUp]}
          dialogTitle={'單位專案總量已達上限'}
          dialogContent={'請聯繫單位管理員刪除專案後，再新增專案'}
          disagreeButtonText={null}
          agreeButtonText={'確定'}
        />
      )}
    </>
  );
}

ReactTable.propTypes = {
  columns: PropTypes.array,
  data: PropTypes.array,
  getHeaderProps: PropTypes.func,
  handleAdd: PropTypes.func
};

const ActionsCell = (row, setTaskData, setLoading, theme, [setPopUp, setPopUpMsg]) => {
  const { data: session } = useSession();
  const userProjectRole = row.original.project_role;

  const { allGroups, setAllGroups, userPermission } = useContext(ConfigContext);
  const [openMoreMenu, setOpenMoreMenu] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [showCheckUtilityReport, setShowCheckUtilityReport] = useState(false);
  // const [popUp, setPopUp] = useState(false);
  // const [popUpMsg, setPopUpMsg] = useState({});
  const [openMemberSelectDialog, setOpenMemberSelectDialog] = useState(false);
  const router = useRouter();

  const [selectedGroup, setSelectedGroup] = useState('機關A'); //選擇專案成員單位
  const [memberOptions, setMemberOptions] = useState([]); //機關下成員選項
  const [selectedMember, setSelectedMember] = useState(null);
  const [selectedMemberId, setSelectedMemberId] = useState(null);
  const [selectedUserRole, setSelectedUserRole] = useState('專案使用者'); //選擇專案成員角色

  const [projectMembers, setProjectMembers] = useState([]); //專案成員表格資料
  const [projectRoles, setProjectRoles] = useState([]); // member_role

  // Get current project_id project_status project_name project_group_id
  const project_id = row.original.project_id;
  const project_status = row.original.project_status;
  const project_name = row.original.project_name;
  const project_group_id = row.original.project_group_id;

  const [group, setGroup] = useState(null); // 列表裡面選擇的某一單位
  const [groupId, setGroupId] = useState(null); // 列表裡面選擇的某一單位ID
  const [userSelectAutocomplete, setUserSelectAutocomplete] = useState(
    <BasicAutocomplete
      options={memberOptions}
      inputValue={selectedMember}
      setInputValue={setSelectedMember}
      setSelectedId={setSelectedMemberId}
      fullWidth
    />
  );

  const handleClick = async (e) => {
    setOpenMoreMenu(true);
    setAnchorEl(e.currentTarget);
    handleCheckUtilityReportList();
  };

  const handleClose = () => {
    console.log('close');
    setOpenMoreMenu(false);
  };

  // Edit project
  const handleProjectEdit = () => {
    router.push({
      pathname: tableRowButtonStatus2URL[project_status],
      query: {
        project_id: project_id,
        project_name: project_name,
        project_group_id: project_group_id
      }
    });
  };
  const handleProjectView = () => {
    router.push({
      pathname: '/apps/project/view-project',
      query: {
        project_id: project_id,
        project_name: project_name,
        project_group_id: project_group_id
      }
    });
  };
  const ButtonEditProject = () =>
    tableRowButtonStatus2URL[project_status] == '' ? (
      <MenuItem disabled>編輯專案</MenuItem>
    ) : (
      <MenuItem onClick={handleProjectEdit}>編輯專案</MenuItem>
    );
  const ButtonViewProject = () => {
    return project_status >= 1 ? <MenuItem onClick={handleProjectView}>檢視專案</MenuItem> : <MenuItem disabled>檢視專案</MenuItem>;
  };
  const ButtonEditViewProject = () => {
    if (handleProjectEditPermission()) {
      return <ButtonEditProject />; // 更多按鈕 > 編輯專案
    } else {
      return <></>; // 更多按鈕 > 編輯專案(for group admin，不能執行專案流程)
    }
  };

  const handleProjectEditPermission = () => {
    // super admin不受project role限制
    if (userPermission.includes('super_admin')) {
      return true;
    } else if(userPermission.length === 0){
      return true;
    }else if (userPermission.length === 1 && userPermission[0] === 'group_admin') {
      return false;
    } else if (userPermission.some((p) => ['group_admin', 'project_admin'].includes(p))) {
      //group_admin 和 project_admin視專案角色決定more選單選項
      if (userProjectRole !== 5) {
        // project admin, project user
        return true;
      } else {
        // data provider
        return false;
      }
    }
  };

  const handleProjectResetDeletePermission = () => {
    if (userPermission.some((p) => ['super_admin', 'group_admin'].includes(p))) {
      return true;
    }
    if (userProjectRole === 3) {
      return true;
    }
    return false;
  };

  const handleProjectResetPermission = () => {
    if (userPermission.includes('super_admin')) {
      return true;
    }
    if (userPermission.length === 1 && userPermission[0] === 'group_admin') {
      return false;
    }
    if (userProjectRole === 3) {
      return true;
    }
    return false;
  };

  // 編輯協作人員相關
  const handleMemberSelect = async () => {
    const promiseResultProjectDetail = await handleGetProjectDetail(session, project_id);
    setPopUpMsg({
      dialogType: 'EditProjectMember',
      projectDetail: promiseResultProjectDetail
    });
    setPopUp(true);
    setOpenMoreMenu(false);
  };

  const handleProjectMemberSelectPermission = () => {
    // super admin不受project role限制
    if (userPermission.includes('super_admin')) {
      return true;
    } else if (userPermission.length === 1 && userPermission[0] === 'group_admin') {
      return false;
    } else if (userPermission.some((p) => ['group_admin', 'project_admin'].includes(p))) {
      //group_admin 和 project_admin視專案角色決定more選單選項
      if (userProjectRole !== 5) {
        // project admin, project user
        return true;
      } else {
        // data provider
        return false;
      }
    } else {
      switch (userProjectRole) {
        case 5:
          // console.log(`Project data provider, project role is:`, userProjectRole);
          return false;
        case 4:
          // console.log(`Project user, project role is:`, userProjectRole);
          return false;
        case 3:
          // console.log(`project admin, project role is:`, userProjectRole);
          return true;
        case 2:
          // console.log(`Group admin, project role is:`, userProjectRole);
          return false;
        case 1:
          // console.log(`Super admin, project role is:`, userProjectRole);
          return true;
        default:
          return false;
      }
    }
  };

  // [TODO] 需新增協作人員編輯頁面
  const ButtonMemberSelect = () => {
    if (handleProjectMemberSelectPermission()) {
      return project_status >= 1 ? (
        <MenuItem onClick={handleMemberSelect}>編輯協作人員</MenuItem>
      ) : (
        <MenuItem disabled>編輯協作人員</MenuItem>
      );
    } else return <></>;
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

  // get project members
  async function getProjectMembers(projectDetail) {
    // console.log('get project members', projectDetail['project_role']);
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
              // console.log('get project members', res);
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
      // console.log('!!! projectMembersList', projectMembersList);
      // console.log('### projectMemberRolesList', projectMemberRolesList);
      setProjectMembers(projectMembersList);
      setProjectRoles(projectMemberRolesList);
    }
  }

  // 重設專案按鈕相關
  const handleResetButton = () => {
    setPopUpMsg({
      dialogType: 'ResetProject',
      dialogTitle: '重設專案',
      dialogContent: '重設專案將清除所有已完成的隱私安全服務強化處理，<br>退回到設定專案的步驟，確定要重設專案?',
      disagreeButtonText: '取消',
      disagreeButtonOnClick: () => {
        setPopUp(false);
        setOpenMoreMenu(false);
      },
      agreeButtonText: '確定',
      agreeButtonOnClick: async () => {
        // Event 1: 重設主系統的專案
        handleProjectReset(session, project_id);

        // Event 2: 重設三個子系統的系統專案
        // 2-1: Get project_eng from projectDetail
        const promiseResultProjectDetail = await handleGetProjectDetail(session, project_id, ['project_eng']);
        const project_eng = promiseResultProjectDetail.project_eng;

        // 2-2: Get k/syn/dp sub-system project_id from checkStatus
        const promiseCheckStatusK = handleFetchSubSystemStatus(session, project_eng, '/api/project/get_k_checkstatus', 'k');
        const promiseCheckStatusSyn = handleFetchSubSystemStatus(session, project_eng, '/api/project/get_syn_checkstatus', 'syn');
        const promiseCheckStatusDP = handleFetchSubSystemStatus(session, project_eng, '/api/project/get_dp_checkstatus', 'dp');
        const promiseListCheckstatus = await Promise.all([promiseCheckStatusK, promiseCheckStatusSyn, promiseCheckStatusDP]);

        // 2-3: Reset k/syn/dp sub-system project with (project_eng & project_id)
        const subsystemResetPromiseList = [];
        if (promiseListCheckstatus[0]['project_status'] > 0)
          subsystemResetPromiseList.push(
            handleResetSubSystemStatus(session, project_eng, promiseListCheckstatus[0]['project_id'], 'KAnonymous')
          );
        if (promiseListCheckstatus[1]['project_status'] > 0)
          subsystemResetPromiseList.push(
            handleResetSubSystemStatus(session, project_eng, promiseListCheckstatus[1]['project_id'], 'syntheticData')
          );
        if (promiseListCheckstatus[2]['project_status'] > 0)
          subsystemResetPromiseList.push(
            handleResetSubSystemStatus(session, project_eng, promiseListCheckstatus[2]['project_id'], 'differentialPrivacy')
          );
        const promiseListReset = subsystemResetPromiseList.length > 0 ? await Promise.all(subsystemResetPromiseList) : null;

        // Event 3: 關閉彈出視窗
        setPopUp(false);
        setOpenMoreMenu(false);
        setLoading(true);
      }
    });
    setPopUp(true);
  };

  const ButtonResetProject = () => {
    if (handleProjectResetPermission()) {
      // super_admin 和 project role的project_admin 可以重設專案
      if (project_status >= 1)
        return <MenuItem onClick={handleResetButton}>重設專案</MenuItem>;
      else
        return <></>;
    } else {
      // 其他都不能重設專案
      // Hind
      return <></>;
    }
  };

  // 刪除專案按鈕相關
  const handleDeleteButton = () => {
    setPopUpMsg({
      dialogType: 'DeleteProject',
      dialogTitle: '刪除專案',
      dialogContent: `確定要刪除專案 ${row.original.project_name}?`,
      disagreeButtonText: '取消',
      disagreeButtonOnClick: () => {
        setPopUp(false);
        setOpenMoreMenu(false);
      },
      agreeButtonText: '確定',
      agreeButtonOnClick: async (event) => {
        const promiseResult = await handleProjectDelete(session, row.original.project_id);
        setLoading(true);
        setPopUp(false);
        setOpenMoreMenu(false);
      }
    });
    setPopUp(true);
  };

  // 更多按鈕 > 刪除專案
  const ButtonDeleteProject = () => {
    if (handleProjectResetDeletePermission()) {
      return <MenuItem onClick={handleDeleteButton}>刪除專案</MenuItem>;
    } else {
      return <></>;
    }
  };

  // 可用性分析按鈕相關
  // Router to page `MLutility`
  const handleGoToUtility = async () => {
    router.push({
      pathname: '/apps/project/MLutility',
      query: {
        project_id: project_id,
        project_name: project_name
      }
    });
  };
  // Child component: showing the button of router to page `MLutility`
  const ButtonGoToUtility = () => {
    // super_admin 和 project_admin 可以執行專案流程
    if (handleProjectEditPermission()) {
      if (project_status == 8)
        // Disabled
        return <MenuItem disabled>可用性分析</MenuItem>;
      else if ((6 <= project_status && project_status < 90) || project_status == 91)
        // Show
        return <MenuItem onClick={handleGoToUtility}>可用性分析</MenuItem>;
      // Hind
      else <></>;
    } // group admin不能執行專案流程
    // Hind
    else return <></>;
  };

  // API: check ML utility report
  const handleCheckUtilityReportList = async () => {
    const config = {
      headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
      params: {
        project_id: project_id
      }
    };
    const promiseResult = await axiosPlus({
      method: 'GET',
      stateArray: null,
      url: '/api/project/get_utility_report_list',
      config: config,
      showSuccessMsg: false
    });

    // console.log(`[handleCheckUtilityReportList] proj_id ${project_id} promiseResult:`, promiseResult);
    if (promiseResult.status == 200 && promiseResult.data.obj.report_info.length > 0) setShowCheckUtilityReport(true);
    else setShowCheckUtilityReport(false);
  };

  // Router to page `utility-report`
  const handleGoToUtilityReport = async () => {
    router.push({
      pathname: '/apps/project/utility-report',
      query: {
        project_id: project_id,
        project_name: project_name
      }
    });
  };

  // Child component: showing the button of router to page `utility-report`
  const ButtonUtilityReport = () => {
    // super_admin 和 project_admin 可以執行專案流程
    if (handleProjectEditPermission()) {
      if (6 <= project_status && project_status < 90) {
        if (showCheckUtilityReport)
          // Show
          return <MenuItem onClick={handleGoToUtilityReport}>可用性分析報表</MenuItem>;
        // else
        //   // Disabled
        //   return <MenuItem disabled>可用性分析報表</MenuItem>;
      }
      // Hind
      else return <></>;
    } else {
      // group admin不能執行專案流程
      return <></>;
    }
  };

  // API: make mlstop status
  const handleEndUtility = async (session, project_id) => {
    const payload = {
      project_id: project_id,
    };
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
    };
    const promiseResult = await axiosPlus({
      method: "PUT",
      stateArray: null,
      url: "/api/project/put_projectMLStop",
      payload: payload,
      config: config,
      showSuccessMsg: false,
    });

    if (promiseResult && promiseResult?.status == 200) {
      // console.log('PUT MLStop success');
    } else {
      // console.log("PUT MLStop fail", promiseResult)
    }

    return promiseResult;
  }

  const handleStopButton = () => {
    setPopUpMsg({
      dialogType: 'StopUtility',
      dialogTitle: '中止可用性分析',
      dialogContent: `確定要中止可用性分析?`,
      disagreeButtonText: '取消',
      disagreeButtonOnClick: () => {
        setPopUp(false);
        setOpenMoreMenu(false);
      },
      agreeButtonText: '確定',
      agreeButtonOnClick: async (event) => {
        const promiseResult = await handleEndUtility(session, row.original.project_id);
        setLoading(true);
        setPopUp(false);
        setOpenMoreMenu(false);
      }
    });
    setPopUp(true);
  }

  // 可用性分析中止按鈕
  const ButtonEndUtility = () => {
    // super_admin 和 project_admin 可以執行專案流程
    if (handleProjectEditPermission()) {
      if (project_status == 8)
        // Disabled
        return <MenuItem onClick={handleStopButton}>可用性分析中止</MenuItem>;
      else if ((6 <= project_status && project_status < 90) || project_status == 91)
        // Show
        return <MenuItem disabled>可用性分析中止</MenuItem>;
      // Hind
      else <></>;
    } // group admin不能執行專案流程
    // Hind
    else return <></>;
  };

  // Render
  return (
    <>
      <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
        <Tooltip title="more">
          <IconButton
            onClick={(e) => {
              handleClick(e);
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
            'aria-labelledby': 'basic-button'
          }}
        >
          {/* <ButtonViewProject /> 更多按鈕 > 檢視專案 */}
          {/* <ButtonEditProject /> 更多按鈕 > 編輯專案 */}
          {/* <ButtonEditViewProject /> */}
          {<ButtonMemberSelect /> /* 更多按鈕 > 編輯協作人員 */}
          {<ButtonResetProject /> /* 更多按鈕 > 重設專案 */}
          {<ButtonGoToUtility /> /* 更多按鈕 > 可用性分析 */}
          {<ButtonEndUtility /> /* 更多按鈕 > 可用性分析中止 */}
          {<ButtonUtilityReport /> /* 更多按鈕 > 可用性分析報表 */}
          {<ButtonDeleteProject /> /* 更多按鈕 > 刪除專案 */}
        </Menu>
      </Stack>
    </>
  );
};

ActionsCell.propTypes = {
  row: PropTypes.object,
  setTaskData: PropTypes.func,
  setOpenConditions: PropTypes.func,
  setLoading: PropTypes.func,
  theme: PropTypes.array,
  stateArray: PropTypes.array
};

// Section Cell and Header
const SelectionHeader = ({ getToggleAllPageRowsSelectedProps }) => (
  <IndeterminateCheckbox indeterminate {...getToggleAllPageRowsSelectedProps()} />
);

SelectionHeader.propTypes = {
  getToggleAllPageRowsSelectedProps: PropTypes.func
};

const ProjectListTable = () => {
  const [clockCount] = useClock({ delay: 10 * 1000, restartState: 0, finalState: 60, increaseStep: 1 }); // Automatic counter, increases by 1 every 5 seconds.
  const theme = useTheme();
  const user = useUser();
  const router = useRouter();
  const { data: session } = useSession();
  const [taskData, setTaskData] = useState([]);
  const [projectList, setProjectList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [renderedTable, setRenderedTable] = useState(<div>wait</div>);
  const [watchList, setWatchList] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [popUp, setPopUp] = useState(false);
  const [popUpMsg, setPopUpMsg] = useState({});

  // Effect clock & reload
  useEffect(() => {
    // Fetch API /projects/list
    handleFetchProjectList(session, [projectList, setProjectList]);
  }, [clockCount, loading]);

  // ReactTable header
  const columns = useMemo(
    () => [
      {
        Header: '專案名稱',
        accessor: 'project_name',
        className: 'cell-center'
      },
      {
        Header: '主責單位',
        accessor: 'project_group_name',
        className: 'cell-center'
      },
      {
        Header: '狀態',
        accessor: 'project_statusname',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '最後修改時間',
        accessor: 'project_time',
        className: 'cell-center',
        //disableSortBy: true
      },
      {
        Header: '更多',
        className: 'download, cell-center',
        disableSortBy: true,
        Cell: ({ row }) => ActionsCell(row, setTaskData, setLoading, theme, [setPopUp, setPopUpMsg])
      }
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );

  // Effect: 每當 project list 更新時，就執行一次
  useEffect(() => {
    // console.log("projectList", projectList);

    // 當沒有對話框時才能自動重整，避免對話框自動消失不見
    if (!popUp) {
      // Render ReactTable
      setRenderedTable(<ReactTable columns={columns} data={projectList} />);

      // Pickout project in connect-processing status
      pickConnectProcessingProjects(session, projectList, [watchList, setWatchList]);
    }
  }, [projectList, popUp]);

  // Effect: 每當 watchList 更新時，就執行一次
  useEffect(() => {
    // console.log("watchList:", watchList);

    // Asynchronous check sub-system status & update project status
    determineChangeStatus(session, watchList);

    // 當沒有對話框時才能自動重整，避免對話框自動消失不見
    if (!popUp)
      // Mark render finished
      setLoading(false);
  }, [watchList]);

  useEffect(() => {
    // 取得登入使用者資訊
    const getUserInfo = async (token) => {
      // console.log('getUserInfo');
      await axios
        .get(`/api/user/get_info/${user.id}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        .then((response) => {
          // console.log('get user info', response.data.obj);
          setUserInfo(response.data.obj);
          if (!response.data.obj.ischange) {
            setPopUpMsg({
              dialogType: 'FirstLogin',
              dialogTitle: '登入成功',
              dialogContent: '首次登入後請前往個人設定頁重設密碼，<br>以開通網站功能',
              disagreeButtonText: null,
              agreeButtonText: '重設密碼',
              agreeButtonOnClick: handlePasswordReset
            });
            setPopUp(true);
          }
        })
        .catch((error) => {
          // console.log('get user info error', error);
        });
    };

    // 取得登入使用者資訊
    getUserInfo(session.tocken.loginUserToken);

    petsLog(session, 0, `Login User ${user.account} 進入專案列表`);
  }, []);

  // 遍歷 projectList 並挑出「隱私鏈結處理中」的專案並存入 watchlist state
  const pickConnectProcessingProjects = async (session, projectList, [watchList, setWatchList]) => {
    // Check project current status (traverse the `projectDetail` array)
    const promiseList = [];
    projectList.map((objProject, index) => {
      const project_status = objProject.project_status;
      const project_id = objProject.project_id;
      if (project_status == 3) {
        const promiseProjectDetail = handleGetProjectDetail(session, project_id, ['project_id', 'project_eng']);
        promiseList.push(promiseProjectDetail);
      }
    });

    // Force to join synchronize all promise
    const promiseResult = await Promise.all(promiseList);
    const watchlist = promiseResult.filter(function (value) {
      return value !== null;
    });
    // console.log("Array of id & engName", watchlist);
    setWatchList(watchlist);
  };

  // Algorithm of determineChangeStatus:
  // 1. 非同步發送所有 request: 遍歷 watchlist，每個專案都打 3 次 (k/syn/dp) 非同步的 request 取得各自的子系統專案狀態，並將 promise 存入 projectsPromiseList.subsystemsPromiseList
  // 2. 同步接收 promiseResult (join): 遍歷 projectsPromiseList，每個專案用 Promise.all 等 3 個子系統的 promiseResult，使回傳結果同步，避免後續判別因資料回傳時間差而出錯
  // 3. 將回傳的狀態 mapping 成 bit signal，透過 bitwise 檢查三個子系統狀態是否 all passed
  const determineChangeStatus = async (session, watchlist) => {
    // subsystem pass status list: K, SYN, DP
    const passStatusList = [3, 2, 2];

    function status2Boolean(status) {
      return status > 0 ? true : false;
    }

    // ===== request sub-system status & determine change project status ===== //

    // console.log("watchlist", watchlist);

    // Request sub-system status (k/gan/dp)
    const projectsPromiseList = [];
    watchlist.map((obj, index) => {
      // console.log(index, obj.project_eng);
      const promiseKStatus = handleFetchSubSystemStatus(session, obj.project_eng, '/api/project/get_k_checkstatus', 'k');
      const promiseGANStatus = handleFetchSubSystemStatus(session, obj.project_eng, '/api/project/get_syn_checkstatus', 'syn');
      const promiseDPStatus = handleFetchSubSystemStatus(session, obj.project_eng, '/api/project/get_dp_checkstatus', 'dp');
      projectsPromiseList.push({
        project_id: obj.project_id,
        project_eng: obj.project_eng, // for debug
        subsystemsPromiseList: [promiseKStatus, promiseGANStatus, promiseDPStatus]
      });
    });

    projectsPromiseList.map(async (obj, index) => {
      // [Notice] If the response is not expected, it might be changed to a for-loop without a map async function.
      // Join: force to synchronize all promise
      const subsystemsPromiseList = obj.subsystemsPromiseList;
      const subsystemStatusList = await Promise.all(subsystemsPromiseList);
      // console.log(
      //   `Project id: ${obj.project_id}\nProject folder name ${obj.project_eng},\n
      // sub-sysyem status array [k, gan, dp]=[${subsystemStatusList[0]['project_status']}, ${subsystemStatusList[1]['project_status']}, ${subsystemStatusList[2]['project_status']}]`,
      //   subsystemStatusList
      // );

      // check the status of all subsystems
      let importErrorFlag = false;
      let allPass = true;
      for (let i = 0; i < subsystemStatusList.length; i++) {
        let bit = 0;
        if (subsystemStatusList[i]['project_status'] == 92) {
          importErrorFlag = true;
          // bit = 0;
        } else bit = status2Boolean(subsystemStatusList[i]['project_status'] >= passStatusList[i] ? 1 : 0);

        // Bitwise AND operation
        allPass = allPass && bit;
      }

      if (importErrorFlag) {
        // Set the project status to 92 if the status of any sub-system is 91.
        const promiseResultUpdateProjStatus = await handleSetProjectStatus(session, obj.project_id, 92);
      } else if (allPass) {
        // Change project status if check all passed
        const promiseResultUpdateProjStatus = await handleSetProjectStatus(session, obj.project_id, 4);
      }
    });
  };

  const handlePasswordReset = () => {
    router.push({
      pathname: '/apps/user/password-reset'
    });
  };

  return (
    <Page title="Customer List">
      <MainCard content={false} sx={{ marginBottom: '100px' }}>
        {/* <ScrollX> */}
        {loading ? '' /* loading... */ : renderedTable}
        {/* </ScrollX> */}
      </MainCard>
      {/* 重設專案、刪除專案、第一次啟用帳號的彈出視窗 */}
      {popUp &&
        (popUpMsg.dialogType == 'ResetProject' ||
          popUpMsg.dialogType == 'DeleteProject' ||
          popUpMsg.dialogType == 'StopUtility' ||
          (popUpMsg.dialogType == 'FirstLogin' && userInfo && !userInfo.ischange)) && (
          <StateControlDialog
            stateArrayOpenControl={[popUp, setPopUp]}
            dialogTitle={popUpMsg.dialogTitle}
            dialogContent={popUpMsg.dialogContent}
            disagreeButtonText={popUpMsg.disagreeButtonText}
            disagreeButtonOnClick={popUpMsg.disagreeButtonOnClick}
            agreeButtonText={popUpMsg.agreeButtonText}
            agreeButtonOnClick={popUpMsg.agreeButtonOnClick}
          />
        )}

      {/* 編輯專案協作人員的彈出視窗 */}
      {popUp && popUpMsg.dialogType == 'EditProjectMember' && (
        <Dialog
          maxWidth="sm"
          fullWidth
          TransitionComponent={PopupTransition}
          onClose={() => {
            setPopUp(false);
          }}
          open={popUp}
          sx={{ '& .MuiDialog-paper': { p: 0 }, transition: 'transform 225ms' }}
        >
          <EditProjectMember
            projectDetail={popUpMsg.projectDetail}
            onCancel={() => {
              setPopUp(false);
            }}
          />
        </Dialog>
      )}
    </Page>
  );
};

ProjectListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default ProjectListTable;
