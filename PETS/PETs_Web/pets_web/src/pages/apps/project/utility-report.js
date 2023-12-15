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
    Typography, Select, MenuItem,
} from '@mui/material';

// project import
import Layout from 'layout';
import Page from 'components/Page';
import UReport from 'sections/apps/report/uti-report';
import axiosPlus from 'sections/api/axiosPlus';
import { reportOptionsDic } from 'data/utility-report';

// ==============================|| UTILITY REPORT PAGE ||============================== //
/**
 * Function: UtilityReport
 *
 * @returns {JSX.Element}
 */
const UtilityReport = () => {
  const router = useRouter();
  const { data: session } = useSession();
  const [project_id, setProject_id] = useState(null);
  const [project_name, setProject_name] = useState(null);
  const [reportOptions, setReportOptions] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [checkReport, setCheckReport] = useState(false);
  const [reportData, setReportData] = useState(null);

  // 測試資料
  // k: project_id=190 system_name=KAnonymous
  // gan: project_id=4 system_name=syntheticData

  // First Mount
  useEffect(() => {
    // Get project_id, project_name, system_name
    setProject_id(router.query.project_id); // [TODO] 接query的參數
  }, []);

  // get project report list and project name
  useEffect(() => {
      if(project_id) {
          const config = {
            headers: {
              Authorization: `Bearer ${session.tocken.loginUserToken}`
            },
            params: {
              project_id : project_id,
            },
          };
          let url = '/api/project/get_utility_report_list';
          const promise = axiosPlus({
            method: "GET",
            stateArray: null,
            url: url,
            config: config,
            showSuccessMsg: false,
          });
          promise.then((response) => {
              setProject_name(response.data.obj.project_name);
              setReportOptions(response.data.obj.report_info);
          });
      }
  }, [project_id]);

  function handleSelectedReport(event) {
      setSelectedReport(event.target.value);
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
          project_id : project_id,
          privacy_type: selectedReport,
        },
      };
      let url = '/api/project/get_utility_report';
      const promise = axiosPlus({
        method: "GET",
        stateArray: null,
        url: url,
        config: config,
        showSuccessMsg: false,
      });

      promise.then(async (response) => {
        await setReportData(response.data.obj);
      });
    }
  }, [project_id, selectedReport]);
  console.log(reportData);

  return (
    <Page title="data report">


      {/*頁面標題 */}
      <Grid container item spacing={3} sx={{ width: '100%', mb: "20px", mt: "150px", ml: "50px" }}>
          <Grid container spacing={12} >
            <Box sx={{ width: '100%', mb: "20px", mt: "50px" }}>
              <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                <Typography variant='h3'>可用性分析報表</Typography>
                <Divider />
              </Stack>
            </Box>
          </Grid>
        </Grid>

      <Grid container spacing={12} sx={{ ml: "50px" }}>
        {/*專案名稱*/}
        <Grid container item spacing={3}>
          <Grid container spacing={12} >
            <Grid item lg={3}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>專案名稱</InputLabel>
            </Grid>
            <Grid item lg={8}>
              <TextField
                disabled
                color="secondary"
                fullWidth
                value={project_name}
              />
            </Grid>
          </Grid>
        </Grid>
        {/*強化資料集報表名稱*/}
        <Grid container item spacing={3}>
          <Grid container spacing={12} >
            <Grid item lg={3}>
              <InputLabel sx={{ textAlign: { xs: 'left', sm: 'left', ml: "250px" } }}>選擇強化資料集報表</InputLabel>
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
                 {reportOptions && reportOptions.map((ro) => {
                    return <MenuItem value={ro.privacy_type}>{reportOptionsDic[ro.privacy_type]}</MenuItem>
                 })}
               </Select>
            </Grid>
            <Grid item lg={1}>
                <Button variant="contained" onClick={() => {setCheckReport(true)}}>查看</Button>
            </Grid>
          </Grid>
        </Grid>
        {(checkReport && selectedReport && reportData) && (
            <>
            <UReport selectedReport={selectedReport} reportData={reportData} />
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
            </>
        )}
      </Grid>
    </Page >
  );
};

UtilityReport.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default UtilityReport;
