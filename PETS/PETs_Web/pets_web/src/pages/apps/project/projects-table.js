import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import axiosPlus from 'sections/api/axiosPlus';
import useClock from 'hooks/useClock';

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
import AlertDialog from 'sections/components-overview/dialogs/AlertDialog';
import CustomAlertDialog from 'sections/apps/Dialog/pop-up-dialog';

// third-party
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';
// import { saveAs } from 'file-saver';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import {
  HeaderSort,
  IndeterminateCheckbox,
  TableRowSelection
} from 'components/third-party/ReactTable';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
// import { mockProjectsList } from '../../../utils/mock-projects-list';
import petsLog from 'sections/apps/logger/insert-system-log';

// assets
import { ConfigContext } from "../../../contexts/ConfigContext";
import { PopupTransition } from "../../../components/@extended/Transitions";
import useUser from "../../../hooks/useUser";
import { LocalizationProvider } from "@mui/x-date-pickers";

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ columns, data }) {
  // console.log('ReactTable', data);
  const theme = useTheme();
  const router = useRouter();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const filterTypes = useMemo(() => renderFilterTypes, []);
  const { userPermission } = useContext(ConfigContext);
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
          {(userPermission.includes('super_admin') || userPermission.includes('project_admin')) && (
            <Stack direction={matchDownSM ? 'column' : 'row'} alignItems="center" spacing={1}>
              <Button sx={{ bgcolor: "#226cea", minWidth: '100px' }} variant="contained" startIcon={<AddIcon />} onClick={handleAdd} size="small">
                建立專案
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
  getHeaderProps: PropTypes.func,
  handleAdd: PropTypes.func,
};

const ActionsCell = (row, setTaskData, setLoading, theme) => {
  const { data: session } = useSession();

  const [openMoreMenu, setOpenMoreMenu] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [showCheckUtilityReport, setShowCheckUtilityReport] = useState(false);

  const router = useRouter();

  // Get current project_id project_status project_name project_group_id
  const project_id = row.original.project_id;
  const project_status = row.original.project_status;
  const project_name = row.original.project_name;
  const project_group_id = row.original.project_group_id;

  const handleClick = async (e) => {
    setOpenMoreMenu(true);
    setAnchorEl(e.currentTarget);
    handleCheckUtilityReportList();
  }

  const handleClose = () => {
    console.log('close');
    setOpenMoreMenu(false);
  }

  // Edit project
  const MappingEditStatus2URL = {
    "0": "/apps/project/edit-project",
    "1": "/apps/project/edit-project",
    "2": "/apps/project/data-check",
    "3": "",
    "4": "/apps/project/privacy-enhancement",
    "5": "/apps/project/privacy-enhancement",
    "6": "/apps/project/privacy-enhancement",
    "7": "/apps/project/privacy-enhancement",
    "8": "/apps/project/privacy-enhancement",
    "9": "/apps/project/privacy-enhancement",
  }
  const handleProjectEdit = () => {
    // Change page with query
    router.push({
      pathname: MappingEditStatus2URL[project_status],
      query: {
        project_id: project_id,
        project_name: project_name,
        project_group_id: project_group_id,
      },
    })
  };
  const buttonEditProject = (MappingEditStatus2URL[project_status] == "") ? <MenuItem disabled>編輯專案</MenuItem> : <MenuItem onClick={handleProjectEdit}>編輯專案</MenuItem>;

  // Reset project status to 1
  const handleProjectReset = async () => {
    // Current project_id 
    console.log(`Reset project_id = ${row.original.project_id}`);
    // API /projects/reset
    const url = "/api/project/put_projectReset";
    const payload = { "project_id": row.original.project_id };
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
    };
    const promiseResult = await axiosPlus({ method: "PUT", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false });
    console.log("API /projects/reset response:\n", promiseResult);

    setLoading(true);
    setOpenMoreMenu(false);
  }

  // Delete project
  const handleProjectDelete = async () => {
    // Get current project_id 
    console.log(`Delete project_id = ${row.original.project_id}`);
    // API /projects/delete
    const url = "/api/project/post_projectDelete";
    const payload = { "project_id": row.original.project_id };
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
    };
    const promiseResult = await axiosPlus({ method: "POST", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false });
    console.log("API /projects/delete response:\n", promiseResult);

    setLoading(true);
    setOpenMoreMenu(false);
  };

  // 可用性分析按鈕相關
  // Router to page `MLutility`
  const handleGoToUtility = async () => {
    router.push({
      pathname: '/apps/project/MLutility',
      query: {
        project_id: project_id,
        project_name: project_name,
      },
    })
  }
  // Child component: showing the button of router to page `MLutility`
  const ButtonGoToUtility = () => {
    if (project_status == 8)
      // Disabled
      return <MenuItem disabled>可用性分析</MenuItem>;
    else if (project_status >= 6)
      // Show
      return <MenuItem onClick={handleGoToUtility}>可用性分析</MenuItem>;
    else
      // Hind
      return <></>;
  }

  // API: check ML utility report
  const handleCheckUtilityReportList = async () => {
    const config = {
      headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
      params: {
        project_id: project_id,
      },
    };
    const promiseResult = await axiosPlus({
      method: "GET",
      stateArray: null,
      url: "/api/project/get_utility_report_list",
      config: config,
      showSuccessMsg: false,
    });

    // console.log(`[handleCheckUtilityReportList] proj_id ${project_id} promiseResult:`, promiseResult);
    if (promiseResult.status == 200 && promiseResult.data.obj.report_info.length > 0)
      setShowCheckUtilityReport(true);
    else
      setShowCheckUtilityReport(false);
  }

  // Router to page `utility-report`
  const handleGoToUtilityReport = async () => {
    router.push({
      pathname: '/apps/project/utility-report',
      query: {
        project_id: project_id,
        project_name: project_name,
      },
    })
  }

  // Child component: showing the button of router to page `utility-report`
  const ButtonUtilityReport = () => {
    if (project_status >= 6) {
      if (showCheckUtilityReport)
        // Show
        return <MenuItem onClick={handleGoToUtilityReport}>可用性分析報表</MenuItem>;
      // else
      //   // Disabled
      //   return <MenuItem disabled>可用性分析報表</MenuItem>;
    }
    else
      // Hind
      return <></>;
  }


  // Render
  return (
    <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
      <Tooltip title="more">
        <IconButton onClick={(e) => { handleClick(e) }}>
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
        {buttonEditProject/* 更多按鈕 > 編輯專案 */}
        <CustomAlertDialog buttonVariant="div" buttonText={"重設專案"} dialogTitle={"重設專案"}
          dialogContent={"重設專案將清除所有已完成的隱私安全服務強化處理，\n退回到設定專案的步驟，確定要重設專案?"}
          disagreeButtonText={"取消"} agreeButtonText={"確定"}
          agreeButtonOnClick={handleProjectReset} />{/* 更多按鈕 > 重設專案 */}
        {<ButtonGoToUtility />  /* 更多按鈕 > 可用性分析 */}
        {<ButtonUtilityReport />/* 更多按鈕 > 可用性分析報表 */}
        <MenuItem onClick={handleProjectDelete}>刪除專案</MenuItem>{/* 更多按鈕 > 刪除專案 */}
      </Menu>
    </Stack>
  );
};

ActionsCell.propTypes = {
  row: PropTypes.object,
  setTaskData: PropTypes.func,
  setOpenConditions: PropTypes.func,
  setLoading: PropTypes.func,
  theme: PropTypes.array,
};

// Section Cell and Header
const SelectionHeader = ({ getToggleAllPageRowsSelectedProps }) => (
  <IndeterminateCheckbox indeterminate {...getToggleAllPageRowsSelectedProps()} />
);

SelectionHeader.propTypes = {
  getToggleAllPageRowsSelectedProps: PropTypes.func
};

const handleFetchProjectList = (session, [projectList, setProjectList]) => {
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    },
  };
  axiosPlus({
    method: "GET",
    stateArray: [projectList, setProjectList],
    url: "/api/project/get_projectList",
    config: config,
    showSuccessMsg: false,
  });
}

// Request project status & eng_name to collect connect-processing projects 
const pickConnectProcessingProjects = async (session, projectList, [watchList, setWatchList]) => {
  // API: fetch project detail (/api/projects/detail)
  const handleFetchProjectEngFromProjectDetail = async (session, project_id) => {
    const payload = {
      project_id: project_id,
    };
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
    };
    const promiseResult = await axiosPlus({
      method: "POST",
      stateArray: null,
      url: "/api/project/post_projectDetail",
      payload: payload,
      config: config,
      showSuccessMsg: false,
    })
    // console.log("EngFromProjectDetail promiseResult", promiseResult);
    if (promiseResult.status == 200 && promiseResult.data.status == true) {
      return {
        project_id: project_id,
        project_eng: promiseResult.data.obj.project_eng
      };
    }
    else
      return null;
  }

  // Check project current status (traverse the `projectDetail` array)
  const promiseList = [];
  projectList.map((objProject, index) => {
    const project_status = objProject.project_status;
    const project_id = objProject.project_id;
    if (project_status == 3)
      promiseList.push(handleFetchProjectEngFromProjectDetail(session, project_id));
  });

  // Force to join synchronize all promise
  const promiseResult = await Promise.all(promiseList);
  const watchlist = promiseResult.filter(function (value) {
    return value !== null;
  });
  // console.log("Array of id & engName", watchlist);
  setWatchList(watchlist);
}

// Request sub-system checkstatus api & bit-wise check all pass
const determineChangeStatus = async (session, watchlist) => {
  // API: fetch sub-system status (/api/project/get_x_checkstatus)
  const handleFetchSubSystemStatus = async (session, project_eng, url, whom) => {
    const config = {
      headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` },
      params: { project_name: project_eng },
    }

    const promiseResult = await axiosPlus({
      method: "GET",
      stateArray: null,
      url: url,
      config: config,
      showSuccessMsg: false,
    })
    // console.log("handleFetchSubSystemStatus promiseResult", promiseResult);
    if (promiseResult.status == 200) {
      if (promiseResult.data[0].status == 1) {
        return promiseResult.data[0].obj.project_status;
      } else {
        console.log(`子系統_${whom} 專案名稱 ${project_eng} 不存在 (或是專案正在建立中):`, promiseResult);
        return -1;
      }
    } else
      // API REQUESTF ERROR: axiosPlus would catch and log
      return 0;
  }

  // API: set new project status (/api/project/put_projectStatus)
  const handleSetProjectStatus = async (session, project_id) => {
    const payload = {
      project_id: project_id,
      status: 4,
    };
    const config = {
      headers: {
        Authorization: `Bearer ${session.tocken.loginUserToken}`
      },
    };
    axiosPlus({
      method: "PUT",
      stateArray: null,
      url: "/api/project/put_projectStatus",
      payload: payload,
      config: config,
      showSuccessMsg: false,
    });
  }

  // subsystem pass status list: K, SYN, DP  
  const passStatusList = [3, 2, 2]; // [TODO-DP] Need to change to DP real status

  function status2Boolean(status) {
    return (status > 0) ? true : false;
  }

  // ===== request sub-system status & determine change project status ===== //

  // console.log("watchlist", watchlist);

  // Request sub-system status (k/gan/dp)
  const projectsPromiseList = [];
  watchlist.map((obj, index) => {
    // console.log(index, obj.project_eng);
    const promiseKStatus = handleFetchSubSystemStatus(session, obj.project_eng, "/api/project/get_k_checkstatus", "k");
    const promiseGANStatus = handleFetchSubSystemStatus(session, obj.project_eng, "/api/project/get_syn_checkstatus", "syn");
    const promiseDPStatus = handleFetchSubSystemStatus(session, obj.project_eng, "/api/project/get_dp_checkstatus", "dp");
    projectsPromiseList.push({
      project_id: obj.project_id,
      subsystemsPromiseList: [promiseKStatus, promiseGANStatus, promiseDPStatus],
    });
  });

  // const returnData = [];
  projectsPromiseList.map(async (obj, index) => { // [Notice] If the response is not expected, it might be changed to a for-loop without a map async function.
    // Join: force to synchronize all promise
    const subsystemsPromiseList = obj.subsystemsPromiseList;
    const subsystemStatusList = await Promise.all(subsystemsPromiseList);
    console.log(`Project id: ${obj.project_id}, sub-sysyem status array [k, gan, dp]:`, subsystemStatusList);

    // check the status of all subsystems
    let result = true;
    for (let i = 0; i < subsystemStatusList.length; i++) {
      const bit = status2Boolean((subsystemStatusList[i] >= passStatusList[i]) ? 1 : 0);
      // Bitwise AND operation  
      result = result && bit;
    }

    // Change project status if check all passed
    if (result) {
      const promiseResultUpdateProjStatus = await handleSetProjectStatus(session, obj.project_id);
    }

    // returnData.push({
    //   project_id: obj.project_id,
    //   subsystems_status: result,
    // });
  });
  // console.log("Check result list:", returnData);
  // return returnData;
}



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

  // Effect clock & reload
  useEffect(() => {
    // Fetch API /projects/list
    handleFetchProjectList(session, [projectList, setProjectList]);
  }, [clockCount, loading])

  // ReactTable header
  const columns = useMemo(
    () => [
      {
        Header: '專案名稱',
        accessor: 'project_name',
        className: 'cell-center'
      },
      {
        Header: '主責機構',
        accessor: 'project_group_name',
        className: 'cell-center',
      },
      {
        Header: '狀態',
        accessor: 'project_statusname',
        className: 'cell-center',
        disableSortBy: true,
      },
      // {
      //   Header: '狀態(debug)',
      //   accessor: 'project_status',
      //   className: 'cell-center',
      //   disableSortBy: true,
      // },
      {
        Header: '最後修改時間',
        accessor: 'project_time',
        className: 'cell-center',
        disableSortBy: true,
      },
      {
        Header: '更多',
        className: 'download',
        disableSortBy: true,
        Cell: ({ row }) => ActionsCell(row, setTaskData, setLoading, theme)
      }
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme]
  );

  const handlePasswordReset = () => {
    router.push({
      pathname: '/apps/user/password-reset'
    });
  }

  // Effect: projectList
  useEffect(() => {
    // console.log("projectList", projectList);
    // Render ReactTable
    setRenderedTable(<ReactTable columns={columns} data={projectList} />);

    // Pickout project in connect-processing status
    pickConnectProcessingProjects(session, projectList, [watchList, setWatchList]);
  }, [projectList])

  useEffect(() => {
    // console.log("watchList:", watchList);

    // Asynchronous check sub-system status & update project status
    determineChangeStatus(session, watchList);

    // Mark render finished
    setLoading(false);
  }, [watchList])

  // 取得登入使用者資訊
  const getUserInfo = async (token) => {
    console.log('getUserInfo');
    await axios.get(`/api/user/get_info/${user.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then((response) => {
        console.log('get user info', response.data.obj);
        setUserInfo(response.data.obj);
        if (!response.data.obj.ischange) {
          setPopUp(true);
        }
      })
      .catch((error) => {
        console.log('get user info error', error);
      });
  };

  useEffect(() => {
    // 取得登入使用者資訊
    getUserInfo(session.tocken.loginUserToken);

    petsLog(session, 0, `Login User ${user.account} 進入專案列表`);
  }, []);

  return (
    <Page title="Customer List">
      <MainCard content={false}>
        <ScrollX>
          {(loading) ? "loading..." : renderedTable}
        </ScrollX>
      </MainCard>
      {(userInfo && !userInfo.ischange) && (
        // 第一次登入提示訊息
        <Dialog open={popUp} onClose={() => { setPopUp(false) }}>
          <DialogTitle>登入成功</DialogTitle>
          <p>首次登入後請前往個人設定頁重設密碼，</p>
          <p>以開通網站功能</p>
          <Button variant="contained" sx={{ bgcolor: "#226cea", minWidth: '100px' }} onClick={handlePasswordReset} >
            重設密碼
          </Button>
        </Dialog>
      )}
    </Page>
  );
};

ProjectListTable.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default ProjectListTable;