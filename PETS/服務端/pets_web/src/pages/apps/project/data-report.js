import { useEffect, useState } from 'react';
import * as React from 'react';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { Box, Button, Divider, Grid, Stack, InputLabel, TextField, Typography } from '@mui/material';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import KReport from 'sections/apps/report/k-report';
import GanReport from 'sections/apps/report/gan-report';
import DpReport from 'sections/apps/report/dp-report';
import axiosPlus from 'sections/api/axiosPlus';
import petsLog from 'sections/apps/logger/insert-system-log';
import useUser from 'hooks/useUser';
import { sub_sys_name } from 'data/sub_system_name';
import { downloadPdfDocument } from 'utils/download-pdf';

// ==============================|| PROJECT REPORT PAGE ||============================== //
/**
 * Function: DataReport
 *
 * @returns {JSX.Element}
 */
const DataReport = () => {
  const router = useRouter();
  const { data: session } = useSession();
  const user = useUser();
  const [projectID, SetProjectID] = useState();
  const [subSystemID, SetSubSystemID] = useState();
  const [projectName, setProjectName] = useState(null);
  const [projectEngName, setProjectEngName] = useState(null);
  const [system_name, setSystem_name] = useState('KAnonymous');
  const [reportData, setReportData] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  // First Mount
  useEffect(() => {
    // Get subSystemID, projectName, system_name
    SetProjectID(router.query.project_id);
    SetSubSystemID(router.query.sub_system_id);
    setProjectName(router.query.project_name);
    setSystem_name(router.query.system_name);
    setProjectEngName(router.query.project_eng_name);
  }, [reportData]);

  useEffect(() => {
    if (subSystemID && system_name) {
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
        params: {
          k_project_id: subSystemID,
          syn_project_id: subSystemID,
          dp_project_id: subSystemID
        }
      };
      let url = '';
      if (system_name === 'KAnonymous') {
        url = '/api/project/get_k_report';
        delete config['params']['syn_project_id'];
        delete config['params']['dp_project_id'];
      } else if (system_name === 'syntheticData') {
        url = '/api/project/get_syn_report';
        delete config['params']['k_project_id'];
        delete config['params']['dp_project_id'];
      }else if(system_name === 'differentialPrivacy'){
        url = '/api/project/get_dp_report';
        delete config['params']['k_project_id'];
        delete config['params']['syn_project_id'];
      }
      console.log('config', config);
      const promise = axiosPlus({
        method: 'GET',
        stateArray: [reportData, setReportData],
        url: url,
        config: config,
        showSuccessMsg: false
      });

      promise.then((response) => {
        // console.log(response.data[0]);
        setReportData(response.data[0]);
        if (!wroteLog['getReport']) {
          petsLog(session, 0, `Login User ${user.account}取得 ${sub_sys_name[system_name]}報表`, projectName);
          setWroteLog((prev) => ({ ...prev, ['getReport']: true }));
        }
      });
    }
  }, [subSystemID]);
  console.log(reportData);

  return (
    <Page title="data report">
      <div id="data-report-to-download">
        {/*頁面標題 */}
        <Grid container spacing={6} sx={{ ml: '50px', maxWidth: '1200px' }}>
          <Grid item>
            <Typography variant="h3" sx={{ marginBottom: '20px',marginTop:'20px' }}>
              專案報表
            </Typography>
          </Grid>
          <Divider />
          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            {/*專案名稱*/}

            <Grid item xs={2} sx={{ marginTop:'10px' }}>
              <InputLabel>專案名稱</InputLabel>
            </Grid>
            <Grid item lg={9}>
              <TextField
                fullWidth
                value={projectName}
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

          {/*專案資料夾名稱*/}
          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            <Grid item xs={2} sx={{ marginTop:'10px' }}>
              <InputLabel>專案資料夾</InputLabel>
            </Grid>
            <Grid item lg={9}>
              <TextField
                fullWidth
                value={projectEngName}
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

          {/*專案Epsilon值*/}
          <Grid container sx={{ margin: '20px 0 0 50px' }}>
            {reportData && reportData.epsilon !== undefined && (
            <>
              <Grid item xs={2} sx={{ marginTop:'10px' }}>
                <InputLabel>專案Epsilon值</InputLabel>
              </Grid>
              <Grid item lg={9}>
                <TextField
                  fullWidth
                  value={reportData ? reportData.epsilon : ''}
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
            </>
            )}
          </Grid>    

          {/*gan報表*/}
          {reportData && system_name === 'syntheticData' && <GanReport reportData={reportData} />}
          {/*dp報表*/}
          {reportData && system_name === 'differentialPrivacy' && <DpReport reportData={reportData} />}
          {/*k報表*/}
          {reportData && system_name === 'KAnonymous' && <KReport reportData={reportData} />}
        </Grid>
      </div>

      <Box display="flex" justifyContent="space-between" sx={{ width: '90%', margin: '0 0 100px 90px' }}>
        <Button
          variant="contained"
          onClick={() => {
            downloadPdfDocument('data-report-to-download', `${projectName}_${sub_sys_name[system_name]}報表`);
          }}
          sx={{ width: '150px', margin: '100px',marginLeft:'10px' }}
        >
          下載報表
        </Button>
        <Button
          variant="contained"
          onClick={() => {
            router.push({
              pathname: '/apps/project/privacy-enhancement',
              query: {
                project_id: projectID,
                project_name: projectName
              }
            });
          }}
          sx={{ width: '150px', margin: '100px',marginRight:'0px' }}
        >
          返回隱私強化選擇
        </Button>
      </Box>
    </Page>
  );
};

DataReport.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default DataReport;
