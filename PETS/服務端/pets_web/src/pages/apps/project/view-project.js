import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import {
  Box,
  Button,
  Divider,
  Grid,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Tooltip,
  TextField,
  Typography,
  IconButton,
  useMediaQuery,
  InputLabel
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import LoadingButton from '@mui/lab/LoadingButton';
import FileCopyOutlinedIcon from '@mui/icons-material/FileCopyOutlined';
import CheckIcon from '@mui/icons-material/Check';
import CircularProgress from '@mui/material/CircularProgress';

// third-party
import axios from 'axios';
import { useExpanded, useFilters, useGlobalFilter, usePagination, useRowSelect, useSortBy, useTable } from 'react-table';

// project import
import MainCard from 'components/MainCard';
import Page from 'components/Page';
import ScrollX from 'components/ScrollX';
import { HeaderSort, TableRowSelection } from 'components/third-party/ReactTable';
import { id_to_join_method_dic } from 'data/join-method';
import { roles_id_member_dic } from 'data/member-role';
import Layout from 'layout';
import axiosPlus from 'sections/api/axiosPlus';
import CustomAlertDialog from 'sections/apps/Dialog/pop-up-dialog';
import ColumnConnect from 'sections/apps/data-connect/column-connect';
import MultiRowTable from 'sections/apps/data-connect/multi-row-table';
import petsLog from 'sections/apps/logger/insert-system-log';
import ProjectStepper from 'sections/apps/progress/project_stepper';
import getALLGroups from 'utils/getGroups';
import getALLUsers from 'utils/getUsers';
import { renderFilterTypes } from 'utils/react-table';
import { ConfigContext } from '../../../contexts/ConfigContext';
import useUser from '../../../hooks/useUser';
import ConnectSetting from '../../../sections/apps/data-connect/connect-setting';
import BasicAutocomplete from '../../../sections/components-overview/autocomplete/BasicAutocomplete';

/***********
 * Control *
 ***********/
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

  if (preprocessJoinFunc && returnObject.join_func.length > 0) {
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
  handleAdd: PropTypes.func
};

const ActionsCopyCell = (row) => {
  // console.log('row in ActionsCell', row);
  const [loading, setLoading] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  const handleCopyKeyCode = async () => {
    if (row.original.key_code) {
      setLoading(true);
      try {
        await navigator.clipboard.writeText(row.original.key_code);
        setIsCopied(true);
        setTimeout(() => {
          setLoading(false);
          setIsCopied(false);
        }, 1000);
      } catch (err) {
        // console.error('複製錯誤',err)
        setLoading(false);
      }
    }
  };

  return (
    <Stack direction="row" alignItems="center" justifyContent="center" spacing={0}>
      {row.original.key_code && (
        <Tooltip title="">
          <span>{row.original.key_code}</span>
          <IconButton onClick={handleCopyKeyCode}>
            {loading ? (
              <CircularProgress size={24} />
            ) : isCopied ? (
              <CheckIcon fontSize="small" />
            ) : (
              <FileCopyOutlinedIcon fontSize="small" />
            )}
          </IconButton>
        </Tooltip>
      )}
    </Stack>
  );
};

/****************
 * View-control *
 ****************/
const ViewProject = () => {
  const theme = useTheme();
  const router = useRouter();
  const user = useUser();
  const { data: session } = useSession();
  const { allUsers, setAllUsers, allGroups, setAllGroups, userPermission } = useContext(ConfigContext); // 所有單位、人員

  const [project_id, setProject_id] = useState(null);
  const [returnURL, setReturnURL] = useState(null);
  const [dataJoinMethod, setDataJoinMethod] = useState('Inner join');
  const [userInfo, setUserInfo] = useState(null);

  const [enckey, setEnckey] = useState(''); //金鑰
  const [firstDownload, setFirstDownload] = useState(true);
  const [keyDownload, setKeydownload] = useState(false);

  const [selectedGroup, setSelectedGroup] = useState('機關A'); //選擇專案成員單位
  const [memberOptions, setMemberOptions] = useState([]); //機關下成員選項
  const [selectedMember, setSelectedMember] = useState(null);
  const [selectedMemberId, setSelectedMemberId] = useState(null);

  const [projectMembers, setProjectMembers] = useState([]); //專案成員表格資料
  const [projectRoles, setProjectRoles] = useState([]); // member_role

  const [dataConnectSettings, setDataConnectSettings] = useState([
    { left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' }
  ]);
  const [columnSettingCount, setColumnSettingCount] = useState(2);
  const [columnSettingContent, setColumnSettingContent] = useState(<></>);
  const [projectDetail, setProjectDetail] = useState(null);
  const [userSelectAutocomplete, setUserSelectAutocomplete] = useState(
    <BasicAutocomplete
      options={memberOptions}
      inputValue={selectedMember}
      setInputValue={setSelectedMember}
      setSelectedId={setSelectedMemberId}
      fullWidth
    />
  );

  // const [canCreateProject, setCanCreateProject] = useState(false);
  const [canOperateProject, setCanOperateProject] = useState(false); // include editing project & executing/viewing data join process
  const [canResetProject, setCanResetProject] = useState(false);
  // const [canDownloadProject, setCanDownloadProject] = useState(false);
  const [canSeeKeycode, setCanSeeKeycode] = useState(false);

  const [wroteLog, setWroteLog] = useState({});
  const [projectStatus, setProjectStatus] = useState(-1);
  const [sampledata, setSampledata] = useState([]);

  const [loading, setLoading] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    // Get project_id
    const _project_id = router.query.project_id;
    setProject_id(_project_id);
    // Get Return url
    setReturnURL(router.query.return_url);
    // Get user role
    getUserInfo(session.tocken.loginUserToken);
    // console.log('project_group_id', router.query.project_group_id);
    getALLGroups(setAllGroups, session.tocken.loginUserToken); // get all groups
    getALLUsers(setAllUsers, session.tocken.loginUserToken); // get all users
    // Get project status
    handleFetchProjectStatus(session, _project_id, setProjectStatus);
    // Fetch API /projects/detail
    handleGetProjectDetail(session, _project_id, [], setProjectDetail);
    // Get sample data
    getSampleData(session.tocken.loginUserToken, _project_id, setSampledata);
  }, []);

  useEffect(() => {
    if (projectDetail) {
      setDataJoinMethod(id_to_join_method_dic[Number(projectDetail.join_type)]);
      getOriDataConnectSettings(projectDetail);
      getProjectMembers(projectDetail);
      if (projectDetail.project_name) {
        if (!wroteLog['enterPage']) {
          petsLog(session, 0, `Login User ${user.account} 進入檢視專案`, projectDetail.project_name);
          setWroteLog((prev) => ({ ...prev, ['enterPage']: true }));
        }
      }

      // 專案的權限設定
      // Project Role 是直接與本專案有關係的角色應最為重要，故先確保自己的 Project role 權限正確。
      // 接著再依系統角色額外開啟相應權限，以只開不關為原則。
      if (projectDetail.project_role) {
        // const MyRoleInThisProject: 我在此專案的專案角色，若為 null 表示本身不屬於此專案
        const filteredArray = projectDetail.project_role.filter((pr) => pr.member_id === user.id);
        const MyRoleInThisProject = filteredArray.length > 0 ? filteredArray[0].project_role : null;

        // 先依照自己是否屬於此專案的角色，開啟 project_role 應有權限
        if (MyRoleInThisProject) {
          switch (MyRoleInThisProject) {
            case 5:
              console.log(`Project data provider, project role is:`, MyRoleInThisProject);
              break;
            case 4:
              console.log(`Project user, project role is:`, MyRoleInThisProject);
              setCanOperateProject(true);
              break;
            case 3:
              console.log(`project admin, project role is:`, MyRoleInThisProject);
              setCanOperateProject(true);
              setCanResetProject(true);
              setCanSeeKeycode(true)
              break;
            case 2:
              console.log(`Group admin, project role is:`, MyRoleInThisProject);
              break;
            case 1:
              console.log(`Super admin, project role is:`, MyRoleInThisProject);
              setCanOperateProject(true);
              setCanResetProject(true);
              setCanSeeKeycode(true)
              break;
            default:
              var assert = require('assert');
              assert(
                !thisUserProjectRole || (1 <= thisUserProjectRole && thisUserProjectRole <= 5),
                `project role 設定錯誤: thisUserProjectRole=${thisUserProjectRole}`
              );
          }
        }

        // 再依照系統角色開啟對應權限
        // if (userPermission.includes('project_admin')) { }
        // if (userPermission.includes('group_admin')) { }
        // console.log("userPermission", userPermission);
        if (userPermission.includes('super_admin')) {
          setCanOperateProject(true);
          setCanResetProject(true);
          setCanSeeKeycode(true)
        }
      }
    }
  }, [projectDetail, userPermission]);

  useEffect(() => {
    // console.log('render cs', dataConnectSettings);
    renderColumnSettingContentForEdit({ columnSettingCount, dataConnectSettings });
  }, [columnSettingCount, dataConnectSettings]);

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
    // console.log('ori BasicAutocomplete');
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
        //disableSortBy: true
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
      }
    ];
    if (canSeeKeycode) {
      columns.push({
        Header: '金鑰識別碼',
        className: 'cell-center no-wrap',
        // disableSortBy: true,
        Cell: ({ row }) => ActionsCopyCell(row)
      });
    }
    return columns;
  }, [theme, projectMembers, projectRoles]);

  /* handle functions */
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
      // console.log('oriDataConnectSettings', oriDataConnectSettings);
      setColumnSettingCount(joinfunc_array.length);
      setDataConnectSettings(oriDataConnectSettings);
    }
  }

  // get project members
  async function getProjectMembers(projectDetail) {
    // console.log('get project members', projectDetail["project_role"]);
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
              temp['key_code'] = pmr.key_code;
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
      // console.log('projectMembersList', projectMembersList);
      setProjectMembers(projectMembersList);
      setProjectRoles(projectMemberRolesList);
    }
  }

  // Preprocess API part 2 - view
  const columnSettingContentForView = (projectDetail) => {
    const content = [];
    if (projectDetail.join_func) {
      const joinFuncList = projectDetail.join_func;
      joinFuncList.map((obj, index) => {
        const tmpArray = [obj.left_datasetname, obj.left_col, obj.right_datasetname, obj.right_col];
        content.push(
          <>
            <Stack direction="row">
              <ColumnConnect columnsMappingList={tmpArray} />
            </Stack>

            <Divider orientation="vertical" flexItem sx={{ margin: '2% 0' }} />
          </>
        );
      });
    }

    return content;
  };
  //  Preprocess API part 2 - edit
  const renderColumnSettingContentForEdit = ({ columnSettingCount, dataConnectSettings }) => {
    // console.log('dataConnectSettings in columnSettingContent', columnSettingCount, dataConnectSettings);
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
              <Stack direction="row" spacing={2}>
                <ConnectSetting dataConnections={dataConnectSettingsTemp} setDataConnections={setDataConnectSettings} index={i} />
              </Stack>
            </Grid>
          </Grid>
        </Grid>
      );
    }
    setColumnSettingContent(content);
    return content;
  };

  const downloadKey = (saveObj) => {
    if (keyDownload || firstDownload) {
      // console.log('download');
      const text = JSON.stringify(saveObj);
      const name = 'project_cert.json';
      const type = 'text/plain';
      // create file
      const a = document.createElement('a');
      const file = new Blob([text], { type: type });
      a.href = URL.createObjectURL(file);
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
    }
  };

  const ButtonResetProject = () => {
    // console.log("canResetProject", canResetProject);
    if (canResetProject && projectDetail) {
      return (
        // super_admin 和 project role的project_admin 可以重設專案
        <CustomAlertDialog
          buttonType="Button"
          buttonVariant="outlined"
          buttonText={'重設專案'}
          dialogTitle={'重設專案'}
          dialogContent={'重設專案將清除所有已完成的隱私安全服務強化處理，\n退回到設定專案的步驟，確定要重設專案?'}
          disagreeButtonText={'取消'}
          agreeButtonText={'確定'}
          agreeButtonOnClick={async () => {
            // Event 1: 重設主系統的專案
            handleProjectReset(session, project_id);

            // Event 2: 重設三個子系統的系統專案
            // 2-1: Get project_eng from projectDetail
            const project_eng = projectDetail.project_eng;

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

            // 3. Go back to project list
            router.push('/apps/project/projects-table');
          }}
        />
      );
    } else {
      // 不能重設專案
      return (
        <Button variant="outlined" sx={{ width: '150px', margin: '100px' }} disabled>
          重設專案
        </Button>
      );
    }
  };

  const ButtonReturn = () => {
    const handlePreviousPage = () => {
      if (returnURL == '/apps/project/privacy-enhancement') {
        router.push({
          pathname: returnURL,
          query: {
            project_id: project_id,
            project_name: projectDetail.project_name
          }
        });
      } else {
        router.push('/apps/project/projects-table');
      }
    };

    return (
      <Button variant="contained" onClick={handlePreviousPage} sx={{ width: '150px', margin: '100px' }}>
        上一步 {/* 返回專案列表, 返回隱私強化選擇 */}
      </Button>
    );
  };

  const createProjectCert = () => {
    const project_certs = {};
    project_certs['group_type'] = userInfo.group_type;
    project_certs['enc_key'] = projectDetail.enc_key;
    // project_certs['project_name'] = projectDetail.project_name;
    project_certs['project_name'] = projectDetail.project_eng;
    project_certs['project_folder'] = projectDetail.project_eng;
    project_certs['pets_service_ip'] = window.location.hostname;
    return { project_cert: btoa(JSON.stringify(project_certs)) };
  };

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

  const handleCopyToClipboard = () => {
    const keyCode = projectDetail?.project_role?.find(role => role.member_id === user.id)?.key_code || '';

    if (keyCode) {
      setLoading(true);
      navigator.clipboard.writeText(keyCode)
        .then(() => {
          setLoading(false);
          setIsCopied(true);  
          setTimeout(() => setIsCopied(false), 2500);
        })
        .catch(err => {
          setLoading(false);
          // console.error('複製失敗: ', err);
        });
    } else {
      // console.error('找不到對應的識別碼')
    }
  };

  /********
   * View *
   ********/
  return (
    <Page title="view project">
      {/* 頂部進度條 */}
      <Box sx={{ width: '750px', margin: '40px auto 60px auto' }}>
        <Box sx={{ width: '100%', alignItems: 'center' }}>
          <ProjectStepper currentStep={projectStatus} terminatedStep={null} />
        </Box>
      </Box>

      {projectDetail && (
        <Grid container spacing={6} sx={{ ml: '50px', maxWidth: '1200px' }}>
          <Grid item>
            <Typography variant="h3" sx={{ marginBottom: '20px' }}>
              查看專案及設定
            </Typography>
          </Grid>
          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>專案名稱</InputLabel>
            </Grid>
            <Grid item xs={8}>
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
            </Grid>
          </Grid>

          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>專案資料夾</InputLabel>
            </Grid>
            <Grid item xs={8}>
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
            </Grid>
          </Grid>

          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>金鑰</InputLabel>
            </Grid>
            <Grid item xs={8}>
              <TextField
                fullWidth
                value={enckey ? enckey : projectDetail.enc_key}
                InputProps={{ readOnly: true, disableUnderline: true }}
                disabled
                multiline
                variant="filled"
                sx={{
                  '& .MuiInputBase-colorPrimary.Mui-disabled': {
                    backgroundColor: 'disableBGColor',
                    padding: '0px'
                  },
                  '& .MuiInputBase-input.Mui-disabled': {
                    WebkitTextFillColor: '#000000',
                    padding: '10px'
                  }
                }}
              />
            </Grid>
           {/*  <Grid item xs={2}>
              <Button
                onClick={() => {
                  setFirstDownload(false);
                  setKeydownload(true);
                  downloadKey(createProjectCert());
                }}
                variant="text"
                startIcon={<FileDownloadOutlinedIcon />}
              >
                下載憑證檔
              </Button>
            </Grid> */}
          </Grid>

          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>協作人員</InputLabel>
            </Grid>
            <Grid item xs={8}>
              <MainCard content={false}>
                <ScrollX>
                  <ReactTable columns={columns} data={projectMembers} />
                </ScrollX>
              </MainCard>
            </Grid>
          </Grid>

          {!canSeeKeycode && (
            <Grid container sx={{ margin: '20px 0 0 50px' }}>
              <Grid item xs={2}>
                <InputLabel>金鑰識別碼</InputLabel>
              </Grid>
              <Grid item xs={8}>
                <TextField
                  fullWidth
                  value={projectDetail?.project_role?.find(role => role.member_id === user.id)?.key_code || ''}
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
              </Grid>
              <Grid item xs={2}>
                <LoadingButton
                  onClick={handleCopyToClipboard}
                  loading={loading} 
                  loadingPosition="start"
                  startIcon={isCopied ? <CheckIcon /> : <FileCopyOutlinedIcon />}
                  variant="text"
                >
                  複製識別碼
                </LoadingButton>
              </Grid>
            </Grid>
          )}

          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>服務端網域名稱</InputLabel>
            </Grid>
            <Grid item xs={8}>
              <TextField
                fullWidth
                value={window.location.hostname}
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
            </Grid>
          </Grid>

          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>服務端目錄名稱</InputLabel>
            </Grid>
            <Grid item xs={8}>
              <TextField
                fullWidth
                value={window.location.pathname}
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
            </Grid>
          </Grid>

          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>資料鏈結方式</InputLabel>
            </Grid>
            <Grid item xs={8}>
              <TextField
                fullWidth
                value={dataJoinMethod}
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
            </Grid>
          </Grid>

          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>資料鏈結欄位屬性設定</InputLabel>
            </Grid>
            <Grid item xs={8}>
              <Stack direction="column" spacing={1} sx={{ minWidth: '95%' }}>
                {projectDetail.join_func ? (
                  columnSettingContentForView(projectDetail)
                ) : (
                  <TextField
                    fullWidth
                    value="尚未設定資料鏈結"
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
                )}
              </Stack>
            </Grid>
          </Grid>

          {canOperateProject && (
            <>
              <Grid container sx={{ margin: '20px 0 0 50px' }}>
                <Grid item xs={2}>
                  <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                    鏈結後的資料集名稱
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <TextField
                    fullWidth
                    value={projectDetail.jointablename}
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
                </Grid>
              </Grid>

              <Grid container sx={{ margin: '20px 0 0 50px' }}>
                <Grid item xs={2}>
                  <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                    資料鏈結筆數
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  <TextField
                    fullWidth
                    value={projectDetail.jointablecount}
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
                </Grid>
              </Grid>

              <Grid container sx={{ margin: '20px 0 0 50px' }}>
                <Grid item xs={2}>
                  <Typography multiline sx={{ textAlign: { xs: 'left', sm: 'left' } }}>
                    資料預覽(僅顯示前20筆資料)
                  </Typography>
                </Grid>
                <Grid item xs={8}>
                  {sampledata.length > 0 ? (
                    <MultiRowTable objectRows={sampledata} tableMinWidth="100%" />
                  ) : (
                    <TextField
                      fullWidth
                      value="尚未進行資料鏈結，無資料可顯示"
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
                  )}
                </Grid>
              </Grid>
            </>
          )}
        </Grid>
      )}

      {/* Buttons */}
      <Box display="flex" justifyContent="space-between" sx={{ width: '100%' }}>
        <ButtonResetProject />
        <ButtonReturn />
      </Box>
    </Page>
  );
};

ViewProject.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default ViewProject;
