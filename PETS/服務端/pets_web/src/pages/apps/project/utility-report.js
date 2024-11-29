import { useEffect, useState } from 'react';
import * as React from 'react';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { Box, Button, Divider, Grid, Stack, InputLabel, TextField, Typography, Select, MenuItem } from '@mui/material';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import UReport from 'sections/apps/report/uti-report';
import axiosPlus from 'sections/api/axiosPlus';
import { reportOptionsDic } from 'data/utility-report';
import petsLog from 'sections/apps/logger/insert-system-log';
import useUser from 'hooks/useUser';
import { downloadPdfDocument } from 'utils/download-pdf';
import { sub_sys_name } from 'data/sub_system_name';

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

// ==============================|| UTILITY REPORT PAGE ||============================== //
/**
 * Function: UtilityReport
 *
 * @returns {JSX.Element}
 */
const UtilityReport = () => {
  const router = useRouter();
  const { data: session } = useSession();
  const user = useUser();
  const [project_id, setProject_id] = useState(null);
  const [project_name, setProject_name] = useState(null);
  const [projectEng, setProjectEng] = useState(null);
  const [reportOptions, setReportOptions] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [checkReport, setCheckReport] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [projectDetail, setProjectDetail] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  // 測試資料
  // k: project_id=190 system_name=KAnonymous
  // gan: project_id=4 system_name=syntheticData

  // First Mount
  useEffect(() => {
    // Get project_id, project_name, system_name
    const _project_id = router.query.project_id;
    setProject_id(_project_id);
    handleGetProjectDetail(session, _project_id, [], setProjectDetail);
  }, []);

  // get projectEng
  useEffect(() => {
    if (projectDetail && !projectEng) setProjectEng(projectDetail.project_eng);
  }, [projectDetail]);

  // get project report list and project name
  useEffect(() => {
    if (project_id) {
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
        params: {
          project_id: project_id
        }
      };
      let url = '/api/project/get_utility_report_list';
      const promise = axiosPlus({
        method: 'GET',
        stateArray: null,
        url: url,
        config: config,
        showSuccessMsg: false
      });
      promise.then((response) => {
        setProject_name(response.data.obj.project_name);
        setReportOptions(response.data.obj.report_info);
      });
    }
  }, [project_id]);

  function handleSelectedReport(event) {
    setSelectedReport(event.target.value);
    setCheckReport(false);
  }

  // get report data
  useEffect(() => {
    console.log('get report data', project_id, selectedReport);
    if (project_id && selectedReport) {
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
        params: {
          project_id: project_id,
          privacy_type: selectedReport
        }
      };
      let url = '/api/project/get_utility_report';
      const promise = axiosPlus({
        method: 'GET',
        stateArray: null,
        url: url,
        config: config,
        showSuccessMsg: false
      });

      promise.then(async (response) => {
        await setReportData(response.data.obj);
        await petsLog(session, 0, `Login User ${user.account}取得 ${reportOptionsDic[selectedReport]}`, project_name);
      });
    }
  }, [project_id, selectedReport]);
  console.log(reportData);

  return (
    <Page title="data report">
      <div id="utility-report-to-download">
        {/*頁面標題 */}
        <Grid container spacing={6} sx={{ ml: '50px', maxWidth: '1200px' }}>
          <Grid item>
            <Typography variant="h3" sx={{ marginBottom: '20px' }}>
              可用性分析報表
            </Typography>
          </Grid>
          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item lg={2}>
              <InputLabel>專案名稱</InputLabel>
            </Grid>
            <Grid item lg={8}>
              <TextField
                fullWidth
                value={project_name}
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
            <Grid item lg={2}>
              <InputLabel>專案資料夾</InputLabel>
            </Grid>
            <Grid item lg={8}>
              <TextField
                fullWidth
                value={projectEng}
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
            <Grid item lg={2}>
              <InputLabel>選擇強化資料集報表</InputLabel>
            </Grid>
            <Grid item lg={8}>
              <Select
                value={selectedReport}
                displayEmpty
                name="select "
                renderValue={(selected) => {
                  return reportOptionsDic[selected];
                }}
                fullWidth
                onChange={handleSelectedReport}
              >
                {reportOptions &&
                  reportOptions.map((ro) => {
                    return <MenuItem value={ro.privacy_type}>{reportOptionsDic[ro.privacy_type]}</MenuItem>;
                  })}
              </Select>
            </Grid>
            <Grid item lg={1}>
              <Button
                variant="contained"
                onClick={() => {
                  setCheckReport(true);
                }}
                sx={{ marginLeft: '20px' }}
              >
                查看
              </Button>
            </Grid>
          </Grid>
          {checkReport && selectedReport && reportData && (
            <>
              <UReport selectedReport={selectedReport} reportData={reportData} />
            </>
          )}
        </Grid>
      </div>
      <Box display="flex" justifyContent="space-between" sx={{ width: '90%', margin: '0 60px 100px 60px' }}>
        <Button
          variant="contained"
          onClick={() => {
            router.push('/apps/project/projects-table');
          }}
          sx={{ width: '150px', margin: '100px' }}
        >
          回到專案列表
        </Button>
        {checkReport && selectedReport && reportData && (
            <Button
              variant="contained"
              onClick={() => {
                downloadPdfDocument('utility-report-to-download', `${project_name}_${reportOptionsDic[selectedReport]}`);
              }}
              sx={{ width: '150px', margin: '100px' }}
            >
              下載報表
            </Button>
        )}

      </Box>
    </Page>
  );
};

UtilityReport.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default UtilityReport;
