import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';
import axiosPlus from 'sections/api/axiosPlus';

// next
import { useSession } from 'next-auth/react';
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
  useMediaQuery,
  DialogTitle,
  Dialog,
  FormControl,
  FormLabel,
  FormControlLabel,
  RadioGroup,
  Radio
} from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import FileDownloadOutlinedIcon from '@mui/icons-material/FileDownloadOutlined';
import LoadingButton from '@mui/lab/LoadingButton';
import FileCopyOutlinedIcon from '@mui/icons-material/FileCopyOutlined';
import CheckIcon from '@mui/icons-material/Check';
import CircularProgress from '@mui/material/CircularProgress';

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
import { HeaderSort, IndeterminateCheckbox, TableRowSelection } from 'components/third-party/ReactTable';
import ProjectStepper from 'sections/apps/progress/project_stepper';
import { roles_id_member_dic } from 'data/member-role';
import { join_method_dic, id_to_join_method_dic } from 'data/join-method';
import petsLog from 'sections/apps/logger/insert-system-log';
// mock data
import { mockMembers } from '../../../utils/mock-members';
import { mockProjectMembers } from '../../../utils/mock-project-members';
import ConnectSetting from '../../../sections/apps/data-connect/connect-setting';
import useUser from '../../../hooks/useUser';
import { ConfigContext } from '../../../contexts/ConfigContext';
import getALLGroups from 'utils/getGroups';
import getALLUsers from 'utils/getUsers';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';
import AddIcon from '@mui/icons-material/Add';
import StateControlDialog from '../../../sections/apps/Dialog/state-dialog';
//import { projectDetail } from '../../../utils/mock-project-detail';

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
    // console.log('POST projectDetail fail', promiseResult);
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
    // console.log('PUT projectStatus success');
  } else {
    // console.log('PUT projectStatus fail', promiseResult);
  }
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
  } else {
    // console.log('POST API projects/sample fail', promiseResult);
  }
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
    // console.log('PUT projectReset success');
    return true;
  } else {
    // console.log('PUT projectReset fail', promiseResult);
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
  else {
    // console.log(`子系統_${whom} 專案名稱 ${project_eng}\nRequest API ERROR`, promiseResult);
  }
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
    // console.log('GET sub-system reset project success');
  } else {
    // console.log('ResetSubSystemStatus send data', requestProps);
    // console.log('GET sub-system reset project fail', promiseResult);
  }

  return promiseResult;
};


// API : fetch project member group (/api/projects/membergroupid)
const handleFetchProjectMemberGroup = async (session, project_id, setProjectGroup) => {
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
    url: '/api/project/get_membergroupid',
    config: config,
    showSuccessMsg: false
  });

  if (promiseResult && promiseResult?.status == 200) {
    setProjectGroup(promiseResult.data.obj)
  } else {
    // console.log("Error", promiseResult)
  }
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

const ActionsCell = (row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles) => {
  // console.log('row in ActionsCell', row);

  const handleClick = () => {
    // console.log('remove member');
  };
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
  setTaskData: PropTypes.func,
  setOpenConditions: PropTypes.func,
  theme: PropTypes.array
};

const ActionsCopyCell = (row, projectDetail) => {
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

// Main Page
const EditProject = () => {
  const theme = useTheme();
  const router = useRouter();
  const user = useUser();
  const { data: session } = useSession();
  const { allUsers, setAllUsers, allGroups, setAllGroups, userPermission, projectGroup, setProjectGroup, status, setStatus, single, setSingle } = useContext(ConfigContext); // 所有單位、人員

  const [userInfo, setUserInfo] = useState(null);
  const [project_id, setProject_id] = useState(null);
  const [dataJoinMethod, setDataJoinMethod] = useState('Inner join');
  const [isDataProvider, setIsDataProvider] = useState(false);

  const [enckey, setEnckey] = useState(''); //金鑰
  const [firstDownload, setFirstDownload] = useState(true);
  const [keyDownload, setKeydownload] = useState(false);

  const [selectedGroup, setSelectedGroup] = useState('機關A'); //選擇專案成員單位
  const [memberOptions, setMemberOptions] = useState([]); //機關下成員選項
  const [selectedMember, setSelectedMember] = useState(null);
  const [selectedMemberId, setSelectedMemberId] = useState(null);
  const [selectedUserRole, setSelectedUserRole] = useState('專案使用者'); //選擇專案成員角色

  const [projectMembers, setProjectMembers] = useState([]); //專案成員表格資料
  const [projectRoles, setProjectRoles] = useState([]); // member_role

  const [responseProjectStatus, setResponseProjectStatus] = useState([]); // 專案狀態 (進度條)

  const [dataConnectSettings, setDataConnectSettings] = useState([
    { left_datasetname: '', left_col: '', right_datasetname: '', right_col: '' }
  ]);
  const [columnSettingCount, setColumnSettingCount] = useState(2);
  const [columnSettingContent, setColumnSettingContent] = useState(<></>);
  const [projectDetail, setProjectDetail] = useState([]);
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
  const [canEditProject, setCanEditProject] = useState(true);
  const [canSeeKeycode, setCanSeeKeycode] = useState(true);

  const [updateStatue, setUpdateStatue] = useState(false);
  const [wroteLog, setWroteLog] = useState({});
  const [projectStatus, setProjectStatus] = useState(-1);

  const [loading, setLoading] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  let project_certs = {};
  const host_ip_address = window.location.hostname;
  // console.log('user group', user.group_id)


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


  useEffect(() => {
    // Get project_id
    const _project_id = router.query.project_id;
    const _project_status = router.query.project_status;
    const _project_singledataset = router.query.isSingleDataset;

    setProject_id(_project_id);
    // Get user info
    getUserInfo(session.tocken.loginUserToken);
    // console.log('project_group_id', router.query.project_group_id);
    getALLGroups(setAllGroups, session.tocken.loginUserToken); // get all groups
    getALLUsers(setAllUsers, session.tocken.loginUserToken); // get all users

    // Get project status
    handleFetchProjectStatus(session, _project_id, setProjectStatus);
    // Fetch API /projects/detail
    handleGetProjectDetail(session, _project_id, [], setProjectDetail, true);

    // Get project member group
    handleFetchProjectMemberGroup(session, _project_id, setProjectGroup)

    setStatus(parseInt(_project_status));
    setSingle(parseInt(_project_singledataset));

  }, [single, status]);
  // console.log("Get the project_id:", project_id);



  const createProjectCert = ({ project_certs }) => {
    project_certs['group_type'] = userInfo.group_type;
    project_certs['enc_key'] = projectDetail.enc_key;
    // project_certs['project_name'] = projectDetail.project_name;
    project_certs['project_name'] = projectDetail.project_eng;
    project_certs['project_folder'] = projectDetail.project_eng;
    project_certs['pets_service_ip'] = window.location.hostname;
    const project_certs_download = { project_cert: btoa(JSON.stringify(project_certs)) };
    //'project_cert_ori' :JSON.parse(atob(btoa(JSON.stringify(project_certs))))
    return project_certs_download;
  };

  useEffect(() => {
    if (project_id) {
      // Change & update project stauts
      handleSetProjectStatus(session, project_id, 1);
      // Get project status
      handleFetchProjectStatus(session, project_id, setProjectStatus);

      // handleFetchProjectMemberGroup(session, _project_id)
    }
  }, [project_id]);

  function getOriDataConnectSettings(projectDetail) {
    // console.log("projectdetail", projectDetail)
    // console.log("projectdetail", projectDetail.single_dataset)
    // console.log("projectdetail", projectDetail.issingle, projectDetail.issingle === 1)
    let oriDataConnectSettings = [];
    if (projectDetail.issingle === 1) {
      if (projectDetail['join_func']) {
        let joinfunc_array = projectDetail['join_func'];
        for (let i = 0; i < joinfunc_array.length; i++) {
          oriDataConnectSettings.push({
            left_datasetname: projectDetail.single_dataset,
            left_col: "",
            right_datasetname: "",
            right_col: ""
          });
        }
        // console.log('oriDataConnectSettings', oriDataConnectSettings);
        setColumnSettingCount(joinfunc_array.length);
        setDataConnectSettings(oriDataConnectSettings);
      }
    } else {
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

  }

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

  useEffect(() => {
    setDataJoinMethod(id_to_join_method_dic[Number(projectDetail.join_type)]);

    getOriDataConnectSettings(projectDetail);
    getProjectMembers(projectDetail);
    if (projectDetail) {
      if (projectDetail.project_name) {
        // console.log("projectDetail", projectDetail);
        if (!wroteLog['enterPage']) {
          petsLog(session, 0, `Login User ${user.account} 進入編輯專案`, projectDetail.project_name);
          setWroteLog((prev) => ({ ...prev, ['enterPage']: true }));
        }
      }
      // 是否能編輯專案的權限設定
      // 沒有任何系統角色的依照project role
      if (!userPermission.some((p) => ['super_admin', 'project_admin', 'group_admin'].includes(p))) {
        if (projectDetail.project_role) {
          // console.log(`project role of ${projectDetail.project_name}`, projectDetail.project_role.filter((pr) => pr.member_id === user.id));
          const projectRoles = projectDetail.project_role.filter((pr) => pr.member_id === user.id);
          if (projectRoles.length > 0 && projectRoles[0].project_role === 5) {
            setCanEditProject(false);
          }
          if(projectRoles.length > 0 && projectRoles[0].project_role === 4){
            setCanSeeKeycode(false)
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
            if (projectDetail.project_role.filter((pr) => pr.member_id === user.id)[0].project_role === 4) {
              setCanSeeKeycode(false)
            }
          }
        }
      }
    }
  }, [projectDetail, userPermission, dataJoinMethod]);

  // Preprocess API
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
  const handleDelete = async (index) => {
    await setColumnSettingCount(columnSettingCount - 1);
    const newDataConnections = [...dataConnectSettings.slice(0, index), ...dataConnectSettings.slice(index + 1)];
    await setDataConnectSettings(newDataConnections);
  };
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
        <Grid container row item>
          <Grid container spacing={12}>
            <Grid item lg={2} />
            <Grid item lg={8} sx={{ marginLeft: '-30px' }}>
              <Stack direction="row" spacing={2}>

                <ConnectSetting dataConnections={dataConnectSettingsTemp} setDataConnections={setDataConnectSettings} index={i} />
                {!(single === 1) && (
                  <IconButton>
                    <RemoveCircleOutlineIcon sx={{ position: 'relative', top: '10px' }} onClick={() => handleDelete(i)} />
                  </IconButton>
                )}
              </Stack>

            </Grid>
          </Grid>
        </Grid>
      );
    }
    setColumnSettingContent(content);
    return content;
  };

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
        // disableSortBy: true
      },
      {
        Header: '角色',
        accessor: 'user_role',
        className: 'cell-center',
        //disableSortBy: true
      }
    ];
    if (canEditProject && canSeeKeycode) {
      columns.push({
        Header: '金鑰識別碼',
        className: 'cell-center no-wrap',
        // disableSortBy: true,
        Cell: ({ row }) => ActionsCopyCell(row, projectDetail)
      });
    }
    if (canEditProject) {
      columns.push({
        Header: '刪除',
        className: 'delete',
        disableSortBy: true,
        Cell: ({ row }) => ActionsCell(row, theme, projectMembers, setProjectMembers, projectRoles, setProjectRoles)
      });
    }
    return columns;
  }, [theme, projectMembers, projectRoles, canEditProject]);

  function getProjectUpdatePayload() {
    // console.log('projectDetail', projectDetail);
    // console.log(projectRoles);
    const payload = JSON.parse(JSON.stringify(projectDetail));
    payload['join_func'] = dataConnectSettings;
    payload['group_id'] = router.query.project_group_id;
    payload['join_type'] = join_method_dic[dataJoinMethod];
    delete payload.Join_func;
    payload.project_role = projectRoles;
    return payload;
  }

  function getProjectUpdatePayloadForSingle() {
    // console.log('projectDetail', projectDetail);
    // console.log(projectRoles);
    const payload = JSON.parse(JSON.stringify(projectDetail));
    payload['join_func'] = dataConnectSettings;
    payload['group_id'] = router.query.project_group_id;
    payload['single_dataset'] = dataConnectSettings[0].left_datasetname;
    delete payload.Join_func;
    payload.project_role = projectRoles;
    return payload;
  }

  // Edit mode to update project data
  const handleCheck = async () => {
    let temp = [];
    await Promise.all(
      await dataConnectSettings.map(async (dc) => {
        // console.log('dc', dc);
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
    // console.log('goSave', goSave, checker(goSave));
    if (checker(goSave)) {
      const url = '/api/project/put_projectUpdate';
      // const payload = projectUpdatePayload; // [TODO] need to fill in dynamic data
      const payload = getProjectUpdatePayloadForSingle();
      // console.log('update payload', payload);
      const config = { headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` } };
      let promiseResult;
      try {
        promiseResult = await axios.post(url, payload, config);
      } catch (error) {
        promiseResult = error.response;
      }
      // const promiseResult = await axiosPlus({ method: "PUT", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false });
      // console.log('API /projects/insert response/error:\n', promiseResult);
      if (promiseResult.status === 400) {
        await setPopUpMsg(promiseResult.data.msg);
        await setCheckPopUp(true);
      }

      // if (!wroteLog['editProject']) {
      //   await petsLog(session, 0, `Login User ${user.account} 編輯專案`, projectDetail.project_name);
      //   setWroteLog((prev) => ({ ...prev, ['editProject']: true }));
      // }
      if (promiseResult.status === 200) {
        if (type === 'save') {
          // Go back to projects-table
          await router.push('/apps/project/projects-table');
        } else {
          // Go to data-check
          await router.push({
            pathname: '/apps/project/data-check',
            query: {
              project_id: project_id,
              project_name: projectDetail.project_name,
              project_eng_name: projectDetail.project_eng,
              isSingleDataset: projectDetail.issingle,
            }
          });
        }
      }
    }
  };

  const handleSingleSave = async (type = 'save') => {
    // Fetch API /projects/updatenew
    // let checker = (arr) => arr.every((v) => v === true);
    // const goSave = await handleCheck();
    // console.log('goSave', goSave, checker(goSave));

    if (single === 1) {
      const url = '/api/project/put_updatenew';
      // const payload = projectUpdatePayload; // [TODO] need to fill in dynamic data
      const payload = getProjectUpdatePayloadForSingle();
      // console.log('update payload', payload);
      const config = { headers: { Authorization: `Bearer ${session.tocken.loginUserToken}` } };
      let promiseResult;
      try {
        promiseResult = await axios.post(url, payload, config);
      } catch (error) {
        promiseResult = error.response;
      }
      // const promiseResult = await axiosPlus({ method: "PUT", stateArray: null, url: url, payload: payload, config: config, showSuccessMsg: false });
      // console.log('API /projects/insert response/error:\n', promiseResult);
      if (promiseResult.status === 400) {
        await setPopUpMsg(promiseResult.data.msg);
        await setCheckPopUp(true);
      }

      if (!wroteLog['editProject']) {
        await petsLog(session, 0, `Login User ${user.account} 編輯專案`, projectDetail.project_name);
        setWroteLog((prev) => ({ ...prev, ['editProject']: true }));
      }
      if (promiseResult.status === 200) {
        if (type === 'save') {
          // Go back to projects-table
          await router.push('/apps/project/projects-table');
        } else {
          // Go to data-check
          await router.push({
            pathname: '/apps/project/data-check',
            query: {
              project_id: project_id,
              project_name: projectDetail.project_name,
              project_eng_name: projectDetail.project_eng,
              isSingleDataset: projectDetail.issingle,
            }
          });
        }
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

  const handleJoinMethodSelect = (event) => {
    setDataJoinMethod(event.target.value);
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


  return (
    <Page title="edit project">
      {/*<MainCard content={false}>*/}
      {/* 頂部進度條 */}
      <Box sx={{ width: '750px', margin: '40px auto 60px auto' }}>
        <Box sx={{ width: '100%', alignItems: 'center' }}>
          <ProjectStepper currentStep={projectStatus} terminatedStep={null} />
        </Box>
      </Box>

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
          <Grid item xs={2}>
            {/* <Button
              onClick={() => {
                setFirstDownload(false);
                setKeydownload(true);
                downloadKey(createProjectCert({ project_certs, host_ip_address }));
              }}
              variant="text"
              startIcon={<FileDownloadOutlinedIcon />}
              sx={{ margainLeft: '30px' }}
            >
              下載憑證檔
            </Button> */}
          </Grid>

          {/* 協作人員下拉選單 */}
          {canEditProject && (
            <Grid container sx={{ marginTop: '20px' }}>
              <Grid item xs={2}>
                <InputLabel>選擇協作人員</InputLabel>
              </Grid>
              <Grid container item xs={8}>
                <Grid item md={3} xs={3}>
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
                </Grid>

                <Grid item md={6} xs={6}>
                  {userSelectAutocomplete}
                  {/*<BasicAutocomplete options={memberOptions} inputValue={selectedMember} setInputValue={setSelectedMember} setSelectedId={setSelectedMemberId} fullWidth />*/}
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
          )}
        </Grid>

        {/* 協作人員表格 */}
        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          {canEditProject ? (
            <Grid item xs={2} />
          ) : (
            <Grid item xs={2}>
              <InputLabel>協作人員</InputLabel>
            </Grid>
          )}
          <Grid item xs={8}>
            <MainCard content={false}>
              <ScrollX>
                <ReactTable columns={columns} data={projectMembers} />
              </ScrollX>
            </MainCard>
          </Grid>
        </Grid>
        
        {!(canEditProject && canSeeKeycode) && (
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

        <Grid container sx={{ margin: '20px 0 0 50px', alignItems: 'center' }}>
          <Grid item xs={2}>
            <InputLabel>是否為單一資料集</InputLabel>
          </Grid>
          <Grid item xs={8} sx={{ margin: '0 0 0 5px' }}>
            <FormControl>
              <RadioGroup
                row
                disabled
                aria-labelledby="demo-row-radio-buttons-group-label"
                name="row-radio-buttons-group"
                value={single}
              // onChange={handleIsSingleDataset}
              >
                <FormControlLabel value={1} disabled control={<Radio />} label="是" />
                <FormControlLabel value={0} disabled control={<Radio />} label="否" />
              </RadioGroup>
            </FormControl>
          </Grid>
        </Grid>

        {!(single === 1) && (
          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2}>
              <InputLabel>資料鏈結方式</InputLabel>
            </Grid>
            {canEditProject ? (
              <Grid item xs={4}>
                <Select
                  fullWidth
                  value={dataJoinMethod}
                  displayEmpty
                  name="select data connect method"
                  renderValue={(selected) => {
                    // return selected;
                    if (selected) {
                      return selected;
                    } else {
                      return dataJoinMethod;
                    }
                  }}
                  onChange={handleJoinMethodSelect}
                >
                  <MenuItem value={'Full outer join'}>Full outer join</MenuItem>
                  <MenuItem value={'Inner join'}>Inner join</MenuItem>
                </Select>
              </Grid>
            ) : (
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
            )}
          </Grid>
        )}

        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item xs={2}>
            <InputLabel>資料鏈結欄位屬性設定</InputLabel>
          </Grid>
          {canEditProject ? (
            <Grid container row sx={{ margin: '0 0 0 10px' }}>
              {dataConnectSettings && columnSettingContent}
            </Grid>
          ) : (
            <Grid container item sx={{ margin: '0 0 0 10px' }}>
              <Grid container item>
                <Grid item xs={2} />
                <Grid item xs={8}>
                  <Stack direction="column" sx={{ minWidth: '100%' }}>
                    (columnSettingContentForView(projectDetail))
                  </Stack>
                </Grid>
              </Grid>
            </Grid>
          )}

        </Grid>

        {!(single === 1) && canEditProject && (
          <Grid container row sx={{ marginTop: '20px' }}>
            <Grid container spacing={6}>
              <Grid item xs={9} />
              <Grid item xs={2}>
                <Button
                  variant="outlined"
                  sx={{ marginLeft: '20px' }}
                  onClick={() => {
                    setColumnSettingCount(columnSettingCount + 1);
                  }}
                  startIcon={<AddIcon />}
                >
                  新增鏈結組合
                </Button>
              </Grid>
            </Grid>
          </Grid>
        )}

        {canEditProject && (
          <>
            <Grid container>
              <Grid container spacing={6}>
                <Grid item xs={9} />
                <Grid item xs={2}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={() => {
                      if (single === 1) {
                        handleSingleSave('save')
                      } else {
                        handleSave('save')
                      }
                    }}
                    sx={{ marginLeft: '20px', marginTop: '40px', width: '200px' }}
                  >
                    儲存設定
                  </Button>
                </Grid>
              </Grid>
            </Grid>
            <Grid container>
              <Grid container spacing={6}>
                <Grid item xs={9} />
                <Grid item xs={2}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={() => {
                      if (single === 1) {
                        handleSingleSave('check')
                      } else {
                        handleSave('check')
                      }
                    }}
                    sx={{ margin: '10px 0 100px 20px', width: '200px' }}
                  >
                    資料匯入及鏈結設定檢查
                  </Button>
                </Grid>
              </Grid>
            </Grid>
          </>
        )}

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
      </Grid>
    </Page>
  );
};

EditProject.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default EditProject;
