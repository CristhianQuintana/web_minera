import http from "k6/http";
import { check, sleep } from "k6";
export const options = {
  stages: [{duration:"15s",target:5},{duration:"15s",target:10},{duration:"10s",target:0}],
  thresholds: { http_req_failed:["rate<0.1"], http_req_duration:["p(95)<800"] },
};
const BASE=__ENV.BASE_URL||"https://web-minera-backend.onrender.com";
const TOKEN=__ENV.TOKEN||"";
export default function(){
  const h = TOKEN?{Authorization:Bearer }:{};
  const health=http.get(${BASE}/health);
  check(health,{ "health200":r=>r.status===200});
  // Sin TOKEN no se afirma capacidad de endpoints de negocio
  if(TOKEN){
    const lots=http.get(${BASE}/api/v1/lots,{headers:h});
    check(lots,{ "lots_ok":r=>r.status===200});
  }
  sleep(1);
}
