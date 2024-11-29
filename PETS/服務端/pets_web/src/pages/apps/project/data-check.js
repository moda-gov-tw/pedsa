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
  Button,
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
import CheckIcon from '@mui/icons-material/Check';

// third-party
import axios from 'axios';
import { useFilters, useExpanded, useGlobalFilter, useRowSelect, useSortBy, useTable, usePagination } from 'react-table';

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
import BasicAutocomplete from '../../../sections/components-overview/autocomplete/BasicAutocomplete';
import { renderFilterTypes, GlobalFilter } from 'utils/react-table';
import DataInfo from "../../../sections/apps/data-connect/data-info";
import ProjectStepper from 'sections/apps/progress/project_stepper';
// mock data
// import { mockProjectMembers } from '../../../utils/mock-project-members';
// import { comparedata } from '../../../utils/mock-compare-data';
import ColumnConnect from 'sections/apps/data-connect/column-connect';
import LinkedDataset from "../../../sections/apps/data-connect/linked-dataset";
import petsLog from "../../../sections/apps/logger/insert-system-log";
import useUser from "hooks/useUser";
import { disableFontColor } from "themes/theme/default.js";

import { ConfigContext } from '../../../contexts/ConfigContext';

/*********** 
 * Control * 
 ***********/
// API: fetch project status (/api/project/get_projectStatus)
const handleFetchProjectStatus = async (session, project_id, setProjectStatus) => {
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`,
    },
    params: {
      project_id: project_id,
    },
  };
  const promiseResult = await axiosPlus({
    method: "GET",
    stateArray: null,
    url: "/api/project/get_projectStatus",
    config: config,
    showSuccessMsg: false,
  });

  if (promiseResult && promiseResult?.status == 200)
    setProjectStatus(promiseResult.data.obj.status);
}

// API: set new project status (/api/project/put_projectStatus)
const handleSetProjectStatus = async (session, project_id, setUpdateStatue) => {
  const payload = {
    project_id: project_id,
    status: 2,
  };
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    },
  };
  const promiseResult = await axiosPlus({
    method: "PUT",
    stateArray: null,
    url: "/api/project/put_projectStatus",
    payload: payload,
    config: config,
    showSuccessMsg: false,
  });

  // console.log("promiseUpdateStatus", promiseResult);
  if (promiseResult && promiseResult.data.status == true)
    setUpdateStatue(true);
}

// API: fetch dataInfo (/api/project/post_projectCompareData)
const handleFetchComparedata = async (session, project_id, setProjectDataInfo, setCompareSuccess, setCompareFailStatus, setErrorMsg, setWaittingCompareData) => {
  const payload = {
    project_id: project_id,
  };
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    },
  };
  const comparedataPromiseResult = await axiosPlus({
    method: "POST",
    stateArray: null,
    url: "/api/project/post_projectCompareData",
    payload: payload,
    config: config,
    showSuccessMsg: false,
  });

  console.log("[API] comparedataPromiseResult", comparedataPromiseResult);

  // store dataInfo
  const status = comparedataPromiseResult.data.status;
  if (comparedataPromiseResult.data.dataInfo)
    setProjectDataInfo(comparedataPromiseResult.data.dataInfo);
  else
    // No dataInfo
    setProjectDataInfo(null);

  if (comparedataPromiseResult.data.status == 0)
    setCompareSuccess(true);
  else {
    console.log("[API] ERROR (comparedata PromiseResult.data):", comparedataPromiseResult.data);
    setCompareSuccess(false);
    setCompareFailStatus(status);
    const returnErrorMsg = comparedataPromiseResult.data.msg;
    let errorSting = ""
    if (status == -1)
      errorSting = errorSting + "錯誤: 沒有 Project id ";
    else if (status == -2)
      errorSting = errorSting + `錯誤: ${returnErrorMsg} `; // "CSV 檔案與 JSON 檔案不一致，或是有缺少檔案 ";
    else if (status == -3)
      errorSting = errorSting + "錯誤: CSV 檔案與 DB 不一致 或是有缺少檔案 ";
    else if (status == -4)
      errorSting = errorSting + "錯誤: 資料不在目錄中 ";
    else // if (status == -5)
      errorSting = errorSting + "未知錯誤 ";
    setErrorMsg(<>{errorSting}</>);
  }

  // Force caller to synchronize
  setWaittingCompareData(false);
}

// API: fetch dataInfo (/api/project/post_compareDataSingle)
const handleFetchComparedataForSingle = async (session, project_id, setProjectDataInfo, setCompareSuccess, setCompareFailStatus, setErrorMsg, setWaittingCompareData) => {
  const payload = {
    project_id: project_id,
  };
  const config = {
    headers: {
      Authorization: `Bearer ${session.tocken.loginUserToken}`
    },
  };
  const comparedataPromiseResult = await axiosPlus({
    method: "POST",
    stateArray: null,
    url: "/api/project/post_compareDataSingle",
    payload: payload,
    config: config,
    showSuccessMsg: false,
  });

  console.log("[API] comparedataPromiseResult", comparedataPromiseResult);

  // store dataInfo
  const status = comparedataPromiseResult.data.status;
  if (comparedataPromiseResult.data.dataInfo)
    setProjectDataInfo(comparedataPromiseResult.data.dataInfo);
  else
    // No dataInfo
    setProjectDataInfo(null);

  if (comparedataPromiseResult.data.status == 0)
    setCompareSuccess(true);
  else {
    console.log("[API] ERROR (comparedata PromiseResult.data):", comparedataPromiseResult.data);
    setCompareSuccess(false);
    setCompareFailStatus(status);
    const returnErrorMsg = comparedataPromiseResult.data.msg;
    let errorSting = ""
    if (status == -1)
      errorSting = errorSting + "錯誤: 沒有 Project id ";
    else if (status == -2)
      errorSting = errorSting + `錯誤: ${returnErrorMsg} `; // "CSV 檔案與 JSON 檔案不一致，或是有缺少檔案 ";
    else if (status == -3)
      errorSting = errorSting + "錯誤: CSV 檔案與 DB 不一致 或是有缺少檔案 ";
    else if (status == -4)
      errorSting = errorSting + "錯誤: 資料不在目錄中 ";
    else // if (status == -5)
      errorSting = errorSting + "未知錯誤 ";
    setErrorMsg(<>{errorSting}</>);
  }

  // Force caller to synchronize
  setWaittingCompareData(false);
}



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
  });
  var returnObject = {};
  if (promiseResult.status == 200 && promiseResult.data.status == true) {
    const projectDetailObject = promiseResult.data.obj;

    // If ColumnFilterList exists, filter promiseResult and return the object of key-value pairs.
    if (returnColumnFilterList.length > 0) {
      returnColumnFilterList.forEach((keyColumn) => {
        returnObject[keyColumn] = projectDetailObject[keyColumn];
      });
    }
    else {
      returnObject = projectDetailObject;
    }
  }
  else {
    console.log("POST projectDetail fail", promiseResult);
    returnObject = null;
  }
  if (setProjectDetail)
    setProjectDetail(returnObject);
  return returnObject;
}

/****************  
 * View-control * 
 ****************/
const DataCheck = () => {
  /* Hooks */
  const router = useRouter();
  const { data: session } = useSession();
  const user = useUser();
  const [gotQuery, setGotQuery] = useState(false);
  const [project_id, setProject_id] = useState(null);
  const [project_name, setProject_name] = useState(null);
  const [project_issingle, setProject_issingle] = useState(null);
  const [projectEng, setProjectEngName] = useState(null);
  const [updateStatue, setUpdateStatue] = useState(false);
  const [projectStatus, setProjectStatus] = useState(-1);
  const [projectDataInfo, setProjectDataInfo] = useState([]);
  const [projectDetail, setProjectDetail] = useState(null);
  const [compareFailStatus, setCompareFailStatus] = useState([]);
  const [compareSuccess, setCompareSuccess] = useState(false);
  const [waittingCompareData, setWaittingCompareData] = useState(true);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [wroteLog, setWroteLog] = useState({});
  const { status, setStatus, single, setSingle } = useContext(ConfigContext); // 所有單位、人員
  const [btnType,setBtnType] = useState(0);

  var matchAll = 1;

  // Mounting effect
  useEffect(() => {
    // Get project_id, project_name
    const _projectId = router.query.project_id;
    const _projectName = router.query.project_name;
    const _projectEng = router.query.project_eng_name;
    const _issingle = router.query.isSingleDataset
    if (_projectName && _projectEng) {
      setProject_name(_projectName);
      setProjectEngName(_projectEng);
    } else {
      handleGetProjectDetail(session, _projectId, [], setProjectDetail).then((_projectDetail) => {
        setProject_name(_projectDetail.project_name);
        setProjectEngName(_projectDetail.project_eng);
      });
    }

    setProject_id(_projectId);
    setProject_issingle(parseInt(_issingle));
    setSingle(parseInt(_issingle));
    setGotQuery(true);

    if(router.query.isSingleDataset === "1"){
      setBtnType("執行隱私強化處理");
    }else{
      setBtnType("執行安全資料鏈結處理")
    }
  }, []);
  // console.log("Get the project_id:", project_id);

  // After mount effect & loading
  useEffect(() => {
    if (project_id) {
      // Update project stauts
      handleSetProjectStatus(session, project_id, setUpdateStatue)

      if(project_issingle === 1){
        handleFetchComparedataForSingle(session, project_id, setProjectDataInfo, setCompareSuccess, setCompareFailStatus, setErrorMsg, setWaittingCompareData)
          .then(() => {
            if (!waittingCompareData && loading) {
              // Call api project detail when fail
              if (compareSuccess) {
                console.log("Compare success!");
                if (!wroteLog["dataCheck"]) {
                  petsLog(session, 0, `Login User ${user.account} 執行資料鏈結設定檢查`, project_name);
                  setWroteLog(prev => ({ ...prev, ["dataCheck"]: true }))
                }
                setLoading(false);
              }
              else {
                console.log("Compare fail!");
                if (!projectDetail) {
                  handleGetProjectDetail(session, project_id, [], setProjectDetail)
                    .then((response) => {
                      setLoading(false);
                    });
                } else {
                  setLoading(false);
                }
              }
            }
          })
      }else{
        // Fetch api /projects/comparedata (dataInfo)
        handleFetchComparedata(session, project_id, setProjectDataInfo, setCompareSuccess, setCompareFailStatus, setErrorMsg, setWaittingCompareData)
          .then(() => {
            if (!waittingCompareData && loading) {
              // Call api project detail when fail
              if (compareSuccess) {
                console.log("Compare success!");
                if (!wroteLog["dataCheck"]) {
                  petsLog(session, 0, `Login User ${user.account} 執行資料鏈結設定檢查`, project_name);
                  setWroteLog(prev => ({ ...prev, ["dataCheck"]: true }))
                }
                setLoading(false);
              }
              else {
                console.log("Compare fail!");
                if (!projectDetail) {
                  handleGetProjectDetail(session, project_id, [], setProjectDetail)
                    .then((response) => {
                      setLoading(false);
                    });
                } else {
                  setLoading(false);
                }
              }
            }
          })
      }

    }
  }, [gotQuery, waittingCompareData])

  // Fetch project status api
  useEffect(() => {
    if (project_id)
      handleFetchProjectStatus(session, project_id, setProjectStatus);
  }, [updateStatue]);

  /* Functions */
  /** Preprocess imported-dataset-table
   * @param {object} api_obj: comparedata (mock data)
   * @returns {JSX.Element}: preprocessedImportedList
   */
  const preprocessedImportedList = (api_obj) => {
    let importList = api_obj.importlist
    // console.log("api_obj", api_obj);
    return (
      <Stack direction="column" spacing={2} margin={1}>
        {importList.map((sample_obj, index) => (
          <div sx={{ width: '100%', overflow: 'hidden' }}>
            {index === 0 ? null : <Divider />}
            <LinkedDataset dataset_name={sample_obj.dataset} dataset_row_count={sample_obj.dataset_count}
              columns={sample_obj.col_setting} columnNames_key="col" />
          </div >
        ))}
      </Stack >
    );
  }

  /** Preprocess compare-data-table
   * @param {object} api_obj: comparedata (mock data)
   * @returns {JSX.Element}: preprocessedCompareData
   */
  const preprocessedCompareData = (api_obj) => {
    let datacompare = api_obj.datacompare;
    // console.log('datacompare', datacompare);
    let content = [];

    datacompare.map((obj, index) => {
      console.log('ds :'+obj.dataset);
      const datasetNames = obj.dataset.split("*");
      console.log("datasetname",datasetNames)
      console.log('col :'+obj.col);
      // const tmpArray = [datasetNames[0], colNames[0], datasetNames[1], colNames[1]];
      
      let tmpArray;

      console.log("tmpArray", tmpArray);
      console.log("obj",obj)

      const mappingMatchString2Num = { "Y": 1, "N": 0 };
      let match;

      if(router.query.isSingleDataset === "1"){
        tmpArray = [obj.dataset,"", "", ""];
        match = obj.match ==="Y"
        matchAll = (matchAll & match);
      }else{
        const colNames = obj.col.split("*");
        tmpArray = [datasetNames[0], colNames[0], datasetNames[1], colNames[1]];
        
        // Current match
        match = mappingMatchString2Num[obj.match] & mappingMatchString2Num[obj.colmatch];
        // Final match all
        matchAll = (matchAll & match);
      }

      content.push(
        <>
          <Stack direction="row">
            <ColumnConnect columnsMappingList={tmpArray} />
            {(match) ? <CheckIcon sx={{ color: 'green', mt: 5 }} /> : <ClearIcon sx={{ color: 'red', mt: 5 }} />}
          </Stack>

          <Divider orientation="vertical" flexItem sx={{ margin: '2% 0' }} />
        </>
      )
    })
    // console.log("matchAll", matchAll);

    return content;
  };

  /** Preprocess compare-data-table (when api comparedata fail)
   * @param {object} api_obj: comparedata (mock data)
   * @returns {JSX.Element}: preprocessedDataDetail
   */
  const preprocessedDataDetail = (api_obj) => {
    const content = [];
    if (projectDetail) {
      // console.log("api_obj:", api_obj);
      const joinFuncList = api_obj.join_func;
      joinFuncList.map((obj, index) => {
        let tmpArray;
        if(router.query.isSingleDataset === "1"){
          tmpArray = [api_obj.single_dataset, obj.left_col, obj.right_datasetname, obj.right_col];
        }else{
          tmpArray = [obj.left_datasetname, obj.left_col, obj.right_datasetname, obj.right_col];
        }
        // const tmpArray = [obj.left_datasetname, obj.left_col, obj.right_datasetname, obj.right_col];
        content.push(
          <>
            <Stack direction="row">
              <ColumnConnect columnsMappingList={tmpArray} />
            </Stack>

            <Divider orientation="vertical" flexItem sx={{ margin: '2% 0' }} />
          </>
        )
      })
    }

    return content;
  };

  /******** 
   * View * 
   ********/
  return (
    <Page title="data check">
      {(loading) ? <>{/* loading */}</> : <>
        {/* 頂部進度條 */}
        <Box sx={{ width: '750px', margin: "40px auto 60px auto" }} >
          <Box sx={{ width: "100%", alignItems: "center" }} >
            <ProjectStepper currentStep={projectStatus} terminatedStep={null} />
          </Box>
        </Box>

        <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
          <Grid container spacing={6} sx={{ ml: "50px" }}>
            <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
              <Grid item>
                <Typography variant='h3' sx={{ marginBottom: "20px" }}>資料匯入及鏈結設定檢查</Typography>
              </Grid>

              <Divider />

              <Grid container item spacing={3}>
                <Grid container spacing={12} >
                  <Grid item lg={2}>
                    <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }} >專案名稱</InputLabel>
                  </Grid>
                  <Grid item lg={8}>
                    <TextField
                      fullWidth
                      value={project_name}
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
                    <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }} >專案資料夾</InputLabel>
                  </Grid>
                  <Grid item lg={8}>
                    <TextField
                      fullWidth
                      value={projectEng}
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

              <Stack direction="column" sx={{ minWidth: '95%' }}>
                <Grid container spacing={10}>
                  {(compareSuccess || projectDataInfo) ?
                    <>
                      <Grid item xs={2}>
                        <Typography variant='h4' fullWidth multiline sx={{ textAlign: { xs: 'left', sm: 'left', ml: "100px" } }}>已匯入資料集</Typography>
                      </Grid>
                      <Grid item xs={8}>
                        {preprocessedImportedList(projectDataInfo) /* <--已匯入資料集的表格 (成功 或 上傳資料不符合) */}
                      </Grid>
                    </> : <>
                      {/* <--- 已匯入資料集的表格 (失敗) */}</>
                  }
                </Grid>
              </Stack>

              <Divider orientation="vertical" flexItem sx={{ margin: '2% 0' }} />

              <Stack direction="column" sx={{ minWidth: '95%' }}>
                <Grid container spacing={10}>
                  <Grid item xs={2}>
                    <Typography variant='h4' fullWidth multiline sx={{ textAlign: { xs: 'left', sm: 'left', ml: "100px" } }}>鏈結欄位檢查</Typography>
                  </Grid>
                  <Grid item xs={8}>
                    <Stack direction="column" spacing={1} sx={{ minWidth: '95%' }}>
                      {(compareSuccess) ? <>
                        {preprocessedCompareData(projectDataInfo) /* <--- 鏈結欄位檢查的表格 (成功) */}</> : <>
                        {preprocessedDataDetail(projectDetail) /* <--- 鏈結欄位檢查的表格 (失敗) */}</>
                      }
                    </Stack>
                  </Grid>
                </Grid>
              </Stack>
            </Stack>
          </Grid>

          {(compareSuccess) ? <></> :
            <Box sx={{ width: '100%', ml: "50px" }}>
              <Typography variant='h4' color="red">{errorMsg}</Typography>
            </Box>
          }

          <Box display="flex" justifyContent="space-between" sx={{ width: '90%' }}>
            <Button
              variant="outlined"
              onClick={() => {
                router.push({
                  pathname: '/apps/project/edit-project',
                  query: {
                    project_id: project_id,
                    project_name: project_name,
                    isSingleDataset: project_issingle,
                  },
                });
              }}
            >
              編輯專案
            </Button>

            {(compareSuccess) ?
              <>
                <Button
                  variant="contained"
                  onClick={() => {
                    router.push({
                      pathname: '/apps/project/data-connect-process',
                      query: {
                        project_id: project_id,
                        project_name: project_name,
                        project_eng_name: projectEng,
                        isSingleDataset: router.query.isSingleDataset
                      },
                    });
                  }}
                  disabled={!matchAll}
                >
                  {btnType}
                </Button>
              </>
              :
              <>
                <Button variant="contained" disabled={true}>{btnType}</Button>
              </>
            }
          </Box>
        </Box>
      </>}
    </Page>
  );
};

DataCheck.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default DataCheck;
