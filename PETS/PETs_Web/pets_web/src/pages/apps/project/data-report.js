import { useEffect, useState } from 'react';
import * as React from 'react';

// next
import { useSession, } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import {
  Box,
  Button,
  Divider,
  Grid,
  Stack,
  InputLabel,
  TextField,
  Typography,
} from '@mui/material';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import KReport from "sections/apps/report/k-report";
import GanReport from "sections/apps/report/gan-report";
import axiosPlus from 'sections/api/axiosPlus';
import petsLog from "sections/apps/logger/insert-system-log";
import useUser from "hooks/useUser";
import { sub_sys_name } from "data/sub_system_name";
import { downloadPdfDocument } from "utils/download-pdf";

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
  const [project_id, setProject_id] = useState();
  const [project_name, setProject_name] = useState(null);
  const [system_name, setSystem_name] = useState('KAnonymous');
  const [reportData, setReportData] = useState(null);
  const [wroteLog, setWroteLog] = useState({});

  // 測試資料
  // k: project_id=190 system_name=KAnonymous
  // gan: project_id=4 system_name=syntheticData

  // First Mount
  useEffect(() => {
    // Get project_id, project_name, system_name
    setProject_id(router.query.sub_system_id); // [TODO] 接query的參數
    setProject_name(router.query.project_name);
    setSystem_name(router.query.system_name);  // [TODO] 接query的參數
  }, []);

  // const get_config = (config) => {
  //   if(system_name==='KAnonymous') {
  //     config[params][]
  //   }
  // }

  useEffect(() => {
    if (project_id && system_name) {
      const config = {
        headers: {
          Authorization: `Bearer ${session.tocken.loginUserToken}`
        },
        params: {
          k_project_id: project_id,
          syn_project_id: project_id
        },
      };
      let url = '';
      if (system_name === 'KAnonymous') {
        url = "/api/project/get_k_report";
        delete config['params']['syn_project_id'];
      } else if (system_name === 'syntheticData') {
        url = "/api/project/get_syn_report";
        delete config['params']['k_project_id'];
      }
      console.log('config', config);
      const promise = axiosPlus({
        method: "GET",
        stateArray: [reportData, setReportData],
        url: url,
        config: config,
        showSuccessMsg: false,
      });

      promise.then((response) => {
        // console.log(response.data[0]);
        setReportData(response.data[0]);
        if (!wroteLog["getReport"]) {
          petsLog(session, 0, `Login User ${user.account}取得 ${sub_sys_name[system_name]}報表`, project_name);
          setWroteLog(prev => ({ ...prev, ["getReport"]: true }))
        }
      });
    }
  }, [project_id]);
  console.log(reportData);

  return (
    <Page title="data report">
      <div id='data-report-to-download'>
        {/*頁面標題 */}
        <Grid container item spacing={3} sx={{ width: '100%', mb: "20px", mt: "150px", ml: "50px" }}>
          <Grid container spacing={12} >
            <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
              <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                <Typography variant='h3'>專案報表</Typography>
                <Divider />
              </Stack>
            </Box>
          </Grid>
        </Grid>

        {/*專案名稱*/}
        <Grid container spacing={12} sx={{ ml: "50px" }}>
          <Grid container item spacing={3}>
            <Grid container spacing={12} >
              <Grid item lg={2}>
                <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案名稱</InputLabel>
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

          {/*gan報表*/}
          {(reportData && system_name === 'syntheticData') && (
            <GanReport reportData={reportData} />
          )}

          {/*k報表*/}
          {(reportData && system_name === 'KAnonymous') && (
            <KReport reportData={reportData} />
          )}
        </Grid>
      </div>

      <Box
        m={1}
        display="flex"
        justifyContent="flex-end"
        alignItems="flex-end"
      >
        <Button
          variant="contained"
          onClick={() => {
            downloadPdfDocument('data-report-to-download', `${project_name}_${sub_sys_name[system_name]}報表`);
          }}
        >
          下載報表
        </Button>
      </Box>

      <Box
        m={1}
        display="flex"
        justifyContent="flex-end"
        alignItems="flex-end"
      >
        <Button
          variant="contained"
          onClick={() => {
            router.push('/apps/project/projects-table');
          }}
        >
          回到專案列表
        </Button>
      </Box>
    </Page >
  );
};

DataReport.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default DataReport;
