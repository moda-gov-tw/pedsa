// import PropTypes from 'prop-types';
// import NextLink from 'next/link';

// material-ui
import * as React from 'react';
import { Box } from '@mui/material';

// project import
// import LogoMain from './LogoMain';
// import LogoIcon from './LogoIcon';
// import { DEFAULT_PATH } from 'config';

// ==============================|| MAIN LOGO ||============================== //

const LogoSection = ({ isIcon }) => {
  // console.log('isIcon', isIcon);
  return (
    <>
      {isIcon ? (
        //<Box component="img" src={'/assets/images/tp-logo-small.jpg'} sx={{ width: '100%', mb: '20px' }} />
        <Box>
          <svg width="40px" height="40px" viewBox="0 -30 200 200">
            <g>
              <path
                fill-opacity="opacity:0.95"
                fill="#0b448f"
                d="M 66.5,30.5 C 82.6715,30.8407 91.6715,39.0073 93.5,55C 92.4526,62.1653 91.4526,69.332 90.5,76.5C 81.5741,78.3203 72.5741,79.1537 63.5,79C 47.1302,72.759 41.6302,61.259 47,44.5C 51.3796,36.7398 57.8796,32.0732 66.5,30.5 Z"
              />
            </g>
            <g>
              <path
                fill-opacity="opacity:0.95"
                fill="#2a6fc8"
                d="M 121.5,30.5 C 140.452,31.616 149.285,41.616 148,60.5C 143.625,75.115 133.792,81.2817 118.5,79C 113.477,78.1073 108.477,77.1073 103.5,76C 101.957,69.0816 100.624,62.0816 99.5,55C 100.792,41.2159 108.126,33.0492 121.5,30.5 Z"
              />
            </g>
            <g>
              <path
                fill-opacity="opacity:0.95"
                fill="#0b448f"
                d="M 66.5,85.5 C 74.1896,86.4481 81.8562,87.6148 89.5,89C 92.3522,97.5984 93.5189,106.432 93,115.5C 88.625,130.115 78.7917,136.282 63.5,134C 47.1302,127.759 41.6302,116.259 47,99.5C 51.3796,91.7398 57.8796,87.0732 66.5,85.5 Z"
              />
            </g>
            <g>
              <path
                fill-opacity="opacity:0.95"
                fill="#0b448f"
                d="M 121.5,85.5 C 140.456,86.6203 149.29,96.6203 148,115.5C 143.625,130.115 133.792,136.282 118.5,134C 106.604,130.434 100.27,122.434 99.5,110C 100.853,103.199 102.019,96.3659 103,89.5C 109.29,88.2985 115.457,86.9652 121.5,85.5 Z"
              />
            </g>
          </svg>
        </Box>
      ) : (
        //<Box component="img" src={'/assets/images/logo.png'} sx={{ width: '100%', pl: '0px', mb: '20px' }} />
        <Box>
          <svg width="180px" viewBox="0 -30 700 200">
            <path
              d="M65.9,44.9c-.8,5.4-1.6,11.3-2.8,17.1-.3,1.2-2,2.8-3.2,3.1-5.9,1.1-11.8,2.3-17.7,2.4-12.1.3-22.1-9-23.2-20.8-1.1-12.5,7.6-23.6,20-25.5,11.6-1.8,23.2,5.8,26.1,17.3.5,1.9.5,3.9.8,6.4Z"
              fill="#0b458f"
              stroke-width="0"
            />
            <path
              d="M77.1,78.9c5.9-1.1,11.5-2.2,17-3,9.6-1.5,19.6,3.7,24.1,12.4,4.7,9.1,2.8,20.4-4.5,27.5-7.2,7-18.3,8.6-27.2,4-8.7-4.5-13.9-14.4-12.4-24,.9-5.5,2-11,3.1-16.9Z"
              fill="#0b458f"
              stroke-width="0"
            />
            <path
              d="M65.7,97.3c-.1,15.9-11.1,25.8-25.5,24.9-12.8-.8-22.6-12.8-21.2-25.8,1.5-13.2,14.4-22.8,27.5-20.4,4.4.8,8.8,1.4,13.2,2.5,1.3.3,3.1,1.6,3.4,2.7,1.2,6,2,12,2.7,16.1Z"
              fill="#0b458f"
              stroke-width="0"
            />
            <path
              d="M120.2,44.3c0,14.5-12.6,25-27.1,22.6-2.6-.4-5.2-1.1-7.8-1.5-8.8-1.4-7.6.4-9.1-9.7-.8-5.3-1.7-10.8-1-16.1,1.7-11.7,13.1-19,23.8-18.2,12.4,1,21.2,10.9,21.2,22.9Z"
              fill="#2a70c8"
              stroke-width="0"
            />
            <g>
              <path
                d="M172.9,85.4v-29.7h59.4v29.7h-25.6v5.4h33.8v6h-33.8v8.8h-8.2v-8.8h-33.8v-6h33.8v-5.4h-25.6ZM169.4,51.3v-17.7h29.4v17.7h-29.4ZM176.7,39.3v6.3h14.8v-6.3h-14.8ZM181.1,61.7v6h17.4v-6h-17.4ZM181.1,73.4v6h17.4v-6h-17.4ZM206.1,51.3v-17.7h29.7v17.7h-29.7ZM224.1,61.7h-17.4v6h17.4v-6ZM206.7,73.4v6h17.4v-6h-17.4ZM213.4,39.3v6.3h15.2v-6.3h-15.2Z"
                fill="#0b458f"
                stroke-width="0"
              />
              <path
                d="M247.5,76.6c-.2-.8-.5-2.1-.9-3.8-.4-1.5-.9-3.9-1.6-7.3,6.3-9.5,11.6-21.3,15.8-35.4l8.5,2.8c-1.9,5.5-4,10.7-6.3,15.8v57.5h-8.2v-41.1c-2.3,4-4.7,7.8-7.3,11.4ZM267.4,102.8v-7.6h26.9c4.8-13.3,9.1-26.3,12.6-39.2l8.8,2.5c-2.3,7.2-6,17.7-11.1,31.6-.8,2.3-1.5,4-1.9,5.1h19v7.6h-54.3ZM269,51.9v-7.9h20.9v-13h8.8v13h21.5v7.9h-51.2ZM282.2,90.2c-2.3-9.3-5.5-19.8-9.5-31.6l8.2-2.2c1.5,4.6,3.8,11.9,7,21.8,1.3,4.2,2.2,7.4,2.8,9.5l-8.5,2.5Z"
                fill="#0b458f"
                stroke-width="0"
              />
              <path d="M335.7,41.2h9.8v47.4h25.5l-1.1,8.1h-34.1v-55.6Z" fill="#0b458f" stroke-width="0" />
              <path
                d="M422.9,68.7c0,16-7.6,28.9-24.7,28.9s-24-12.9-24-28.9,7.5-28.2,24.7-28.2,24,12.9,24,28.2ZM384.3,68.6c0,11.8,4.7,21,14.3,21s14.2-8.8,14.2-20.9-4-20.3-14.3-20.3-14.1,9-14.1,20.2Z"
                fill="#0b458f"
                stroke-width="0"
              />
              <path
                d="M476.4,96.8h-7.3c-.4-1.7-.6-4.2-.8-7-2.9,5.8-8.4,7.8-15.7,7.8-14.5,0-22-12.2-22-28.3s8.8-28.8,24.9-28.8,19.5,7,21,16.5h-9.6c-1.3-4.4-4.1-8.5-11.9-8.5s-14.3,9.6-14.3,20.9,4,20.3,14,20.3,12-6.7,12-14.9v-.3h-12.6v-8.4h22.3v30.7Z"
                fill="#0b458f"
                stroke-width="0"
              />
              <path
                d="M535,68.7c0,16-7.6,28.9-24.7,28.9s-24-12.9-24-28.9,7.5-28.2,24.7-28.2,24,12.9,24,28.2ZM496.4,68.6c0,11.8,4.7,21,14.3,21s14.2-8.8,14.2-20.9-4-20.3-14.3-20.3-14.1,9-14.1,20.2Z"
                fill="#0b458f"
                stroke-width="0"
              />
            </g>
          </svg>
        </Box>
      )}
    </>
  );
  // <NextLink href={!to ? DEFAULT_PATH : to} passHref>
  //   <ButtonBase disableRipple sx={sx}>
  //     {isIcon ? <LogoIcon /> : <LogoMain reverse={reverse} />}
  //   </ButtonBase>
  // </NextLink>
};

export default LogoSection;
