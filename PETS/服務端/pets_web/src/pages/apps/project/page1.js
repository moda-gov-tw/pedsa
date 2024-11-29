import { useRef } from 'react';

// next
import { useRouter } from 'next/router';

// material-ui
import { Grid } from '@mui/material';

// project import
import Layout from 'layout';

// ==============================|| PROFILE - USER ||============================== //

const ProjectsList = () => {
  // const inputRef = useRef(null);
  //
  // const focusInput = () => {
  //   inputRef.current?.focus();
  // };
  //
  // const router = useRouter();
  // const { tab } = router.query;

  return (
    <div>
        <p>first page</p>
        <p>first page123</p>
    </div>
  );
};

ProjectsList.getLayout = function getLayout(page) {
  return <Layout>{page}</Layout>;
};

export default ProjectsList;
