// import { useSelector } from 'react-redux';

// material-ui
// import { useTheme } from '@mui/material';

// project import
// import NavCard from './NavCard';
import Navigation from './Navigation';
import SimpleBar from 'components/third-party/SimpleBar';

// ==============================|| DRAWER CONTENT ||============================== //

const DrawerContent = () => {
  // console.log('DrawerContent');
  // const theme = useTheme();
  // const matchDownMD = useMediaQuery(theme.breakpoints.down('lg'));

  // const menu = useSelector((state) => state.menu);
  // console.log('menu', menu);
  // const { drawerOpen } = menu;

  return (
    <SimpleBar
      sx={{
        '& .simplebar-content': {
          display: 'flex',
          flexDirection: 'column'
        }
      }}
    >
      <Navigation />
      {/*{drawerOpen && !matchDownMD && <NavCard />}*/}
    </SimpleBar>
  );
};

export default DrawerContent;
