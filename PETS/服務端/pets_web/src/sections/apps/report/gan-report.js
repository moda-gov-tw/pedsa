// material-ui
import { Grid, Stack, Typography } from '@mui/material';

// project import
import MainCard from '../../../components/MainCard';
import ScrollX from '../../../components/ScrollX';
import ReportTable from 'sections/apps/report/report-table';
import { ganColDic } from 'data/gan-report-columns';

// ==============================|| PROJECT - GAN REPORT ||============================== //
/**
 * Function: GanReport
 *
 * Child component of DataReport
 *
 * @param {{ reportData: object }} argObject
 * * `reportData`: value of report data.
 *
 * @returns {JSX.Element}
 */
const GanReport = ({ reportData }) => {

  let synDataDict = {};
  reportData.syndata_info.forEach(item => {
      synDataDict[item.col_name] = item;
  });
  
  reportData.rawdata_info.forEach(item => {
      if (synDataDict[item.col_name]) {
          item.syn_col_value = synDataDict[item.col_name].col_value;
      }
  });

  return (
    <>
      {/*gan報表-原始資料（raw）*/}

      <Grid container sx={{ margin: '20px 0 0 50px' }}>
        <Grid item lg={2} />
        <Grid item lg={9}>
          <Stack direction="column" spacing={1} sx={{ minWidth: '90%', margin: '20px 0' }}>
            <Typography variant="h4">原始資料與合成資料統計資訊比較</Typography>
            <MainCard content={false}>
              <ScrollX>
                <ReportTable columns={Object.keys(ganColDic)} rows={reportData.rawdata_info} colDic={ganColDic} />
              </ScrollX>
            </MainCard>
          </Stack>
        </Grid>
      </Grid>
    </>
  );
};

export default GanReport;
