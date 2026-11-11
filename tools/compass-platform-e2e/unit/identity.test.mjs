import {test} from 'node:test'
import assert from 'node:assert/strict'
import vm from 'node:vm'
import {readFileSync} from 'node:fs'
import {ROOT} from '../support/settings.mjs'
import {join} from 'node:path'
const script=readFileSync(join(ROOT,'support/freight-capture.js'),'utf8')
const tick=()=>new Promise(r=>setImmediate(r))
async function identity(app,host,enterprise){
 const window={location:{href:app},fetch:async()=>new Response(JSON.stringify({code:200,data:{userId:'fixture-user',...(enterprise?{enterpriseDetailResponse:{enterpriseId:'fixture-company'}}:{})}}))}
 vm.runInNewContext(script,{window,URL,Request,Response,TextDecoder,Date})
 await window.fetch(host+'/whale-user-center/whale/user/get-user-detail-info')
 for(let i=0;i<10;i++)await tick()
 return window.__compassE2E.identity
}
test('真实环境身份路由：Dev iter、Beta apisix、Prod whale-ingress；个人用户允许企业为空',async()=>{
 assert.equal((await identity('https://dev-smart-agent.hgj.com/query','https://iter-apisix.hgj.com',false)).enterpriseId,null)
 assert.equal((await identity('https://beta-smart-agent.hgj.com/query','https://beta-apisix.hgj.com',true)).enterpriseId,'fixture-company')
 assert.equal((await identity('https://qianxun.hgj.com/query','https://whale-ingress-ng.hgj.com',true)).userId,'fixture-user')
 assert.equal(await identity('https://qianxun.hgj.com/query','https://beta-apisix.hgj.com',true),null)
})
