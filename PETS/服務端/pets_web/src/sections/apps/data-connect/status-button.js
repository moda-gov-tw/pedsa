import PropTypes from 'prop-types';
import { useContext, useEffect, useMemo, useState } from 'react';
import * as React from 'react';

// next
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Button, Typography } from '@mui/material';

/**
 * Function StatusButton
 *
 * @param {{ currentStatus:Number, triggrtStatus:Number, buttonName:String, url:String, minHeight:String, changeStatusFunc:Function, propChangeStatus:Object }} argObject
 * * `currentStatus`: current status of button. set status -1 to disabled button.
 * * `triggrtStatus`: if currentStatus >= triggrtStatus, then disable = false.
 * * `buttonName`
 * * `url`
 * * `minHeight`
 * @returns {JSX.Element}
 */
export default function StatusButton({
  currentStatus = -1,
  triggrtStatus = 0,
  buttonName = 'button',
  minHeight = '33%',
  onClickFunc = null
}) {
  // View
  if (currentStatus < triggrtStatus)
    return (
      <Button
        variant="outlined"
        style={{ 'pointer-events': 'none', cursor: 'default' }}
        sx={{ minHeight: minHeight, '&:hover': { backgroundColor: '#f0f7fe' } }}
        disabled
      >
        <Typography variant="h4" style={{ color: 'black' }}>
          {buttonName}
        </Typography>
      </Button>
    );
  else
    return (
      <Button
        variant="outlined"
        onClick={onClickFunc}
        sx={{ minHeight: minHeight, borderColor: 'gray', '&:hover': { backgroundColor: '#f0f7fe' } }}
      >
        <Typography variant="h4" style={{ color: 'black' }}>
          {buttonName}
        </Typography>
      </Button>
    );
}
