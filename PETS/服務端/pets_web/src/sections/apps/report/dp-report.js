// material-ui
import { Grid, Stack, Typography } from '@mui/material';

// project import
import MainCard from '../../../components/MainCard';
import ScrollX from '../../../components/ScrollX';
import ReportTable from 'sections/apps/report/report-table';
import { dpColDic } from 'data/dp-report-columns';

// ==============================|| PROJECT - dp REPORT ||============================== //
/**
 * Function: dpReport
 *
 * Child component of DataReport
 *
 * @param {{ reportData: object }} argObject
 * * `reportData`: value of report data.
 *
 * @returns {JSX.Element}
 */
const DpReport = ({ reportData }) => {

  let dpDataDict = {};
  reportData.syndata_info.forEach(item => {
      dpDataDict[item.col_name] = item;
  });
  
  reportData.rawdata_info.forEach(item => {
      if (dpDataDict[item.col_name]) {
          item.dp_col_value = dpDataDict[item.col_name].col_value;
      }
  });

  return (
    <>
      {/*dp報表-原始資料（raw）*/}

      <Grid container sx={{ margin: '20px 0 0 50px' }}>
        <Grid item lg={2} />
        <Grid item lg={9}>
          <Stack direction="column" spacing={1} sx={{ minWidth: '90%', margin: '20px 0' }}>
            <Typography variant="h4">原始資料與差分資料統計資訊比較</Typography>
            <MainCard content={false}>
              <ScrollX>
                <ReportTable columns={Object.keys(dpColDic)} rows={reportData.rawdata_info} colDic={dpColDic} />
              </ScrollX>
            </MainCard>
          </Stack>
        </Grid>
      </Grid>

    </>
  );
};

export default DpReport;
