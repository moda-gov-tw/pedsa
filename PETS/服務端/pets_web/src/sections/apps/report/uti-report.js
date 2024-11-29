import { useEffect, useState } from 'react';

// material-ui
import { Divider, Grid, Stack, Typography } from '@mui/material';

// project import
import MainCard from 'components/MainCard';
import ScrollX from 'components/ScrollX';
import ReportTable from 'sections/apps/report/report-table';
import { reportOptionsDic, uColDic } from 'data/utility-report';

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
const UReport = ({ selectedReport, reportData }) => {
  const [priTitle, setProTitle] = useState('');
  const [title, setTitle] = useState("");

  useEffect(() => {
    if (selectedReport === 'k') {
      setProTitle('K/K 由K匿名資料建模，K匿名資料做驗證');
    }
    if (selectedReport === 'syn') {
      setProTitle('syn./syn. 由合成資料建模，合成資料做驗證');
      setTitle("syn./raw. 由合成資料建模，原始資料做驗證")
    }
    if (selectedReport === 'dp') {
      setProTitle('dp./dp. 由差分資料建模，差分資料做驗證');
      setTitle("dp./raw. 由差分資料建模，原始資料做驗證")
    }
  }, [selectedReport]);

  function getPrivacyData(data, col) {
    return data.filter((d) => d.colName === col)[0].result;
  }
  function getUtilityLevel(data, col) {
    const item = data.filter((d) => d.colName === col)[0];
    return item ? item.utilitylevel : '';
  }

  function translateUtilityLevel(level) {
    switch (level) {
      case 'Low':
        return '低';
      case 'Medium':
        return '中';
      case 'High':
        return '高';
      default:
        return level;
    }
  }

  return (
    <>
      {/*utility報表-標題*/}
      <Grid container sx={{ margin: '20px 0 0 50px' }}>
        <Grid item lg={2} />
        <Grid item lg={8}>
          <Typography variant="h4" sx={{ marginTop: '20px' }}>
            {reportOptionsDic[selectedReport]}
          </Typography>
          <Divider />
        </Grid>
      </Grid>

      {/*utility報表-報表表格*/}
      {reportData.rawData.map((d) => (
        <Grid container sx={{ margin: '20px 0 0 50px' }}>
          <Grid item lg={2} />
          <Grid item lg={8}>
            <Typography variant="h5" sx={{ color: '#096dd9', marginTop: '20px' }}>{`感興趣欄位: ${d.colName}`}</Typography>

            <Typography variant="h6" sx={{ fontWeight: '600' }}>{`raw /raw 由原始資料建模，原始資料做驗證`}</Typography>
            <MainCard content={false} sx={{ margin: '10px 0 20px 0' }}>
              <ScrollX>
                <ReportTable columns={Object.keys(uColDic)} rows={d.result} colDic={uColDic} />
              </ScrollX>
            </MainCard>

            {reportData.privacyData?.length > 0 && (
              <>

                <Typography variant="h6" sx={{ fontWeight: '600' }}>

                  {priTitle}
                </Typography>
                {selectedReport !== 'k' && (
                  <Typography variant="h6" sx={{ fontWeight: '600' }}>
                    可用性指標 :{' '}
                    <span style={{ color: 'red' }}>
                      {translateUtilityLevel(getUtilityLevel(reportData.privacyrawData, d.colName))}
                    </span>
                  </Typography>
                )}
                <MainCard content={false} sx={{ margin: '10px 0 20px 0' }}>
                  <ScrollX>
                    <ReportTable columns={Object.keys(uColDic)} rows={getPrivacyData(reportData.privacyData, d.colName)} colDic={uColDic} />
                  </ScrollX>
                </MainCard>
              </>
            )}

            {reportData.privacyrawData?.length > 0 && (
              <>
                <Typography variant="h6" sx={{ fontWeight: '600' }}>
                  {title}
                </Typography>
                {selectedReport !== 'k' && (
                  <Typography variant="h6" sx={{ fontWeight: '600' }}>
                    可用性指標 :{' '}
                    <span style={{ color: 'red' }}>
                      {translateUtilityLevel(getUtilityLevel(reportData.privacyrawData, d.colName))}
                    </span>
                  </Typography>
                )}
                <MainCard content={false} sx={{ margin: '10px 0 20px 0' }}>
                  <ScrollX>
                    <ReportTable columns={Object.keys(uColDic)} rows={getPrivacyData(reportData.privacyrawData, d.colName)} colDic={uColDic} />
                  </ScrollX>
                </MainCard>
              </>
            )}

          </Grid>
        </Grid>
      ))}
    </>
  );
};

export default UReport;
