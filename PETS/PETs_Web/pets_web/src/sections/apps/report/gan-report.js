// material-ui
import {
    Grid,
    Stack,
    Typography
} from "@mui/material";

// project import
import MainCard from "../../../components/MainCard";
import ScrollX from "../../../components/ScrollX";
import ReportTable from "sections/apps/report/report-table";
import { ganColDic } from "data/gan-report-columns";

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
const GanReport = ({reportData}) => {

    return (
        <>
            {/*gan報表-原始資料（raw）*/}
            <Grid container item spacing={3}>
              <Grid container spacing={12} >
                <Grid item lg={8}>
                  <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                    <Typography variant='h3'>原始資料（ raw )</Typography>
                    <MainCard content={false}>
                      <ScrollX>
                        <ReportTable columns={Object.keys(ganColDic)} rows={reportData.rawdata_info} colDic={ganColDic}/>
                      </ScrollX>
                    </MainCard>
                  </Stack>
                </Grid>
              </Grid>
            </Grid>

            {/*gan報表-合成資料（syn)*/}
            <Grid container item spacing={3}>
              <Grid container spacing={12} >
                <Grid item lg={8}>
                  <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                    <Typography variant='h3'>合成資料（ syn )</Typography>
                    <MainCard content={false}>
                      <ScrollX>
                        <ReportTable columns={Object.keys(ganColDic)} rows={reportData.syndata_info} colDic={ganColDic}/>
                      </ScrollX>
                    </MainCard>
                  </Stack>
                </Grid>
              </Grid>
            </Grid>
        </>
    )
}

export default GanReport;