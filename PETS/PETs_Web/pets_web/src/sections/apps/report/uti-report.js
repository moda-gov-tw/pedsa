import { useEffect, useState } from 'react';

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
import { reportOptionsDic, uColDic } from "data/utility-report";

// ==============================|| PROJECT - K REPORT ||============================== //
/**
 * Function: UReport
 *
 * Child component of UtilityReport
 *
 * @param {{ selectedReport: string, reportData: object }} argObject
 * * `selectedReport`: value of selected report type. ex: 合成資料可用性分析報表
 * * `reportData`: value of report data.
 *
 * @returns {JSX.Element}
 */
const UReport = ({selectedReport, reportData}) => {
    const [priTitle, setProTitle] = useState('');

    useEffect(() => {
        if(selectedReport==='k') {
            setProTitle('K/K 由K匿名資料建模，K匿名資料做驗證');
        }
        if(selectedReport==='syn') {
            setProTitle('syn./syn. 由合成資料建模，合成資料做驗證');
        }
    }, [selectedReport]);

    function getPrivacyData(data, col) {
        return data.filter((d) => d.colName === col)[0].result;
    }

    return (
        <>
            {/*utility報表-標題*/}
            <Grid container item spacing={3}>
              <Grid container spacing={12} >
                <Grid item lg={8}>
                  <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                      <Typography variant='h3'>{reportOptionsDic[selectedReport]}</Typography>
                      <Divider />
                  </Stack>
                </Grid>
              </Grid>
            </Grid>

            {/*utility報表-報表表格*/}
            {reportData.rawData.map((d) => (
                <Grid container item spacing={3}>
                  <Grid container spacing={12} >
                    <Grid item lg={8}>
                      <Stack direction="column" spacing={1} sx={{ minWidth: '90%' }}>
                          <Typography variant='h3'>{`感興趣欄位: ${d.colName}`}</Typography>
                          <Typography variant='h3'>{`raw /raw 由原始資料建模，原始資料做驗證`}</Typography>
                          <MainCard content={false}>
                              <ScrollX>
                                <ReportTable columns={Object.keys(uColDic)} rows={d.result} colDic={uColDic}/>
                              </ScrollX>
                          </MainCard>
                          <Typography variant='h3'>{priTitle}</Typography>
                          <MainCard content={false}>
                              <ScrollX>
                                <ReportTable columns={Object.keys(uColDic)} rows={getPrivacyData(reportData.privacyData, d.colName)} colDic={uColDic}/>
                              </ScrollX>
                          </MainCard>
                      </Stack>
                    </Grid>
                  </Grid>
                </Grid>
            ))}
        </>
    )
}

export default UReport;