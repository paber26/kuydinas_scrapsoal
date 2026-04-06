const axios = require('axios');

async function test() {
  try {
    const res = await axios.post('https://apikuy.kuydinas.id/api/admin/login', {
      email: 'admin@gmail.com',
      password: '12345678'
    });
    console.log('Status:', res.status);
    console.log('Data:', res.data);
  } catch (err) {
    console.log('Error Status:', err.response?.status);
    console.log('Error Data Snippet:', err.response?.data?.toString().substring(0, 500));
    console.log('Error Message:', err.message);
  }
}

test();
