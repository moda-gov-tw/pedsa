import * as React from 'react';

// material-ui
import {
  Grid,
  Stack,
  TextField,
} from '@mui/material';
import OpenInFullRoundedIcon from '@mui/icons-material/OpenInFullRounded';

// ==============================|| REACT TABLE ||============================== //

function GroupColumnSelect({ selectedGroup = '', selectedColumn = '' }) {

  return (
    <>
      <Grid container spacing={1} sx={{ 'flex-direction': 'column' }} >
        <Grid item>
          <TextField
            disabled
            fullWidth
            value={selectedGroup}
            InputProps={{ readOnly: true, disableUnderline: true }}
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

        <Grid item>
          <TextField
            disabled
            fullWidth
            value={selectedColumn}
            InputProps={{ readOnly: true, disableUnderline: true }}
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
    </>
  );
}

/**
 * Function: ColumnConnect
 *
 * Child component of EditProject
 *
 * @param {{ columnsMappingList: string }} argObject
 * * `columnsMappingList`: all data connections in the project.
 *
 * @returns {JSX.Element}
 */
const ColumnConnect = ({ columnsMappingList = '' }) => {
  console.log('columnsMappingList', columnsMappingList);
  let gn1 = String(columnsMappingList[0]);
  let col1 = String(columnsMappingList[1]);
  let gn2 = String(columnsMappingList[2]);
  let col2 = String(columnsMappingList[3]);

  return (
    <Grid container spacing={2} columns={10}>
      <Grid item md={4}>
        <GroupColumnSelect selectedGroup={gn1} selectedColumn={col1} />
      </Grid>
      <Grid container item md={2} justifyContent="center" alignItems='center'>
        <OpenInFullRoundedIcon sx={{ "transform": "rotate(45deg)", 'position': "relative", 'top': "-1px" }} />
      </Grid>
      <Grid item md={4}>
        <GroupColumnSelect selectedGroup={gn2} selectedColumn={col2} />
      </Grid>
    </Grid>
  );
};

export default ColumnConnect;
