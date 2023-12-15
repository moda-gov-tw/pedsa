// project import
import Layout from 'layout';
import Page from 'components/Page';
import Landing from 'sections/landing';
// import { headers } from 'next/headers';

export default function HomePage() {
  // const nonce = headers().get('x-nonce');nonce={nonce}
  return (
    <Page title="Landing" >
      <Landing />
    </Page>
  );
}

HomePage.getLayout = function getLayout(page) {
  return <Layout variant="auth">{page}</Layout>;
};
