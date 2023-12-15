import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';
import * as React from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
  Grid,
  IconButton,
  TextField,
} from '@mui/material';
import OpenInFullRoundedIcon from '@mui/icons-material/OpenInFullRounded';
import ClearIcon from '@mui/icons-material/Clear';

// ==============================|| COLUMN SELECT ||============================== //

// function ColumnSelect({ start=false, firstColumn=false, prevSelect='', setPrevSelect=() => {}, groups = []}) {
/**
 * Function: ColumnSelect
 *
 * Child component of ConnectSetting
 *
 * @param {{ first: boolean, data: string, setData: func, column: string, setColumn: func, dataConnections: object, setDataConnections: func, index: number }} argObject
 * * `first`: whether it's the left dataset and column.
 * * `data`: dataset name.
 * * `setData`: function to update dataset name.
 * * `column`: column name.
 * * `setColumn`: function to update column name.
 * * `dataConnections`: all data connections in the project.
 * * `setDataConnections`: function for updating dataConnections.
 * * `index`: indxe of the current data connection.
 *
 * @returns {JSX.Element}
 */
function ColumnSelect({ first = true, data = '', setData = () => { }, column = '', setColumn = () => { }, dataConnections, setDataConnections, index }) {

  const handleData = (event) => {
    setData(event.target.value);
    let newDataConnection = [...dataConnections];
    // console.log('newDataConnection[index]', newDataConnection[index]);
    if (first) {
      newDataConnection[index] = {
        ...newDataConnection[index],
        left_datasetname: event.target.value,
      };
    } else {
      newDataConnection[index] = {
        ...newDataConnection[index],
        right_datasetname: event.target.value,
      };
    }
    setDataConnections(newDataConnection);
  };

  const handleColumn = (event) => {
    setColumn(event.target.value);
    let newDataConnection = [...dataConnections];
    // console.log('newDataConnection[index]', newDataConnection[index]);
    if (first) {
      newDataConnection[index] = {
        ...newDataConnection[index],
        left_col: event.target.value,
      };
    } else {
      newDataConnection[index] = {
        ...newDataConnection[index],
        right_col: event.target.value,
      };
    }
    setDataConnections(newDataConnection);
  };

  return (
    <>
      <Grid container spacing={1} sx={{ 'flex-direction': 'column' }} >
        <Grid item>
          <TextField
            fullWidth
            value={data}
            onChange={handleData}
          />
        </Grid>

        <Grid item>
          <TextField
            fullWidth
            value={column}
            onChange={handleColumn}
          />
        </Grid>
      </Grid>

    </>
  );
}

/**
 * Function: ConnectSetting
 *
 * Child component of NewProjectDataConnect
 *
 * @param {{ dataConnections: object, setDataConnections: func, index: number }} argObject
 * * `dataConnections`: all data connections in the project.
 * * `setDataConnections`: function for updating dataConnections.
 * * `index`: indxe of the current data connection.
 *
 * @returns {JSX.Element}
 */
const ConnectSetting = ({ dataConnections, setDataConnections, index }) => {
  const theme = useTheme();
  // console.log('dataConnections in ConnectSetting', dataConnections, index);
  // console.log(dataConnections[index]);

  const [firstData, setFirstData] = useState(dataConnections[index].left_datasetname);
  const [firstColumn, setFirstColumn] = useState(dataConnections[index].left_col);
  const [secondData, setSecondData] = useState(dataConnections[index].right_datasetname);
  const [secondColumn, setSecondColumn] = useState(dataConnections[index].right_col);

  useEffect(() => {
    if(dataConnections[index]) {
      // console.log('set the data');
      setFirstData(dataConnections[index].left_datasetname);
      setFirstColumn(dataConnections[index].left_col);
      setSecondData(dataConnections[index].right_datasetname);
      setSecondColumn(dataConnections[index].right_col)
    }
  }, [dataConnections])

  // useEffect(() => {
  //   if(index && dataConnections[index]) {
  //     console.log('update dataConnections');
  //     console.log('ori dataConnections', [...dataConnections]);
  //     let newDataConnection = [...dataConnections];
  //     console.log('newDataConnection[index]', newDataConnection[index]);
  //     newDataConnection[index] = {
  //       ...newDataConnection[index],
  //       firstData: firstData,
  //       firstColumn: firstColumn,
  //       secondData: secondData,
  //       secondColumn: secondColumn
  //     }
  //     setDataConnections(newDataConnection);
  //   }
  //   console.log('dataConnections', dataConnections);
  // }, [firstData, firstColumn, secondData, secondColumn]);

  return (
    <Grid container spacing={2} columns={10}>
      <Grid item md={4}>
        <ColumnSelect first={true} data={firstData} setData={setFirstData} column={firstColumn} setColumn={setFirstColumn} dataConnections={dataConnections} setDataConnections={setDataConnections} index={index} />
      </Grid>
      <Grid container item md={2} justifyContent="center" alignItems='center'>
        <OpenInFullRoundedIcon sx={{ "transform": "rotate(45deg)", 'position': "relative", 'top': "-1px" }} />
      </Grid>
      <Grid item md={4}>
        <ColumnSelect first={false} data={secondData} setData={setSecondData} column={secondColumn} setColumn={setSecondColumn} dataConnections={dataConnections} setDataConnections={setDataConnections} index={index} />
      </Grid>
    </Grid>
  );
};

export default ConnectSetting;


{/*舊的ColumnSelect 選機關(第二組機關選項不會有第一組已經選好的機關)*/ }
{/*{start ? (*/ }
{/*    <TextField*/ }
{/*        fullWidth*/ }
{/*        defaultValue="機關A"*/ }
{/*        InputProps={{*/ }
{/*          readOnly: true,*/ }
{/*        }}*/ }
{/*    />*/ }
{/*) : (*/ }
{/*    <FormControl fullWidth>*/ }
{/*      <InputLabel id="group-select-label">機關</InputLabel>*/ }
{/*      <Select*/ }
{/*            value={selectedGroup}*/ }
{/*            displayEmpty*/ }
{/*            name="select group"*/ }
{/*            onChange={handleChange}*/ }
{/*            renderValue={(selected) => {*/ }
{/*              return selected;*/ }
{/*            }}*/ }
{/*            // onChange={handleChange}*/ }
{/*          >*/ }
{/*          {groupOptions.map((group) => {*/ }
{/*            return <MenuItem value={group} onClick={handleClose}>{group}</MenuItem>*/ }
{/*          })}*/ }
{/*      </Select>*/ }
{/*    </FormControl>*/ }
{/*)}*/ }
