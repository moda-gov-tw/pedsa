// material-ui
import {
    Divider,
    Grid,
    Stack,
    Typography
} from "@mui/material";

// project import
import MainCard from "components/MainCard";
import ScrollX from "components/ScrollX";
import ReportTable from "sections/apps/report/report-table";
import {kColDic1, kColDic2, kColDic3} from "data/k-report-columns";

// ==============================|| PROJECT - K REPORT ||============================== //
/**
 * Function: KReport
 *
 * Child component of DataReport
 *
 * @param {{ reportData: object }} argObject
 * * `reportData`: value of report data.
 *
 * @returns {JSX.Element}
 */
const KReport = ({reportData}) => {

    return (
        <>
            {/*k報表-資料集資訊*/}
            <Grid container item spacing={3}>
              <Grid container spacing={12} >
                <Grid item lg={8}>
                  <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                      <Typography variant='h3'>資料彙整與評估</Typography>
                      <Divider />
                      <Typography variant='h3'>資料集名稱: {reportData.datasetInfo.ds_name}</Typography>
                      <MainCard content={false}>
                        <ScrollX>
                          <ReportTable columns={Object.keys(kColDic1)} rows={[reportData.datasetInfo]} colDic={kColDic1} />
                        </ScrollX>
                      </MainCard>
                  </Stack>
                </Grid>
              </Grid>
            </Grid>

            {/*k報表-資料處理結構*/}
            <Grid container item spacing={3}>
              <Grid container spacing={12} >
                <Grid item lg={8}>
                  <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                    <Typography variant='h3'>資料處理結構</Typography>
                    <Divider />
                    <Typography variant='h3'>表格: {reportData.datasetInfo.ds_name}</Typography>
                    <MainCard content={false}>
                      <ScrollX>
                        <ReportTable columns={Object.keys(kColDic2)} rows={reportData.dataStructure} colDic={kColDic2}/>
                      </ScrollX>
                    </MainCard>
                  </Stack>
                </Grid>
              </Grid>
            </Grid>

            {/*k報表-有隱私洩漏風險的資料筆數*/}
            <Grid container item spacing={3}>
                <Grid container spacing={12} >
                  <Grid item lg={8}>
                    <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                      <Typography variant='h3'>有隱私洩漏風險的資料筆數</Typography>
                      <Divider />
                      <Typography variant='h3'>資料集名稱: {reportData.datasetInfo.ds_name}</Typography>
                      <MainCard content={false}>
                        <ScrollX>
                          <ReportTable columns={Object.keys(kColDic3)} rows={reportData.warnning_col} colDic={kColDic3} />
                        </ScrollX>
                      </MainCard>
                    </Stack>
                  </Grid>
                </Grid>
            </Grid>
        </>
    )
}

export default KReport;