import { test } from 'node:test'
import assert from 'node:assert/strict'
import {mkdtempSync, readFileSync, writeFileSync, chmodSync, symlinkSync, realpathSync} from 'node:fs'
import {tmpdir} from 'node:os'
import {join} from 'node:path'
import {saveAuth,loadAuth,assertIdentity} from '../support/auth-store.mjs'
const identity={userId:'u1',enterpriseId:'e1'}
const storage={cookies:[{domain:'.hgj.com',name:'fixture',value:'secret-test-value'}],origins:[{origin:'https://dev-smart-agent.hgj.com',localStorage:[]}]}
const root=()=>mkdtempSync(join(realpathSync(tmpdir()),'compass-auth-unit-'))
test('认证状态加密、跨环境拒绝、身份切换不覆盖、原子写入',()=>{
 const dir=root();saveAuth('dev',identity,storage,dir)
 assert.equal(loadAuth('dev',dir).storage.cookies[0].value,'secret-test-value')
 assert.equal(readFileSync(join(dir,'dev.json'),'utf8').includes('secret-test-value'),false)
 assert.equal(loadAuth('beta',dir),null)
 assert.throws(()=>saveAuth('dev',{...identity,userId:'other'},storage,dir),/MISMATCH/)
 assert.equal(loadAuth('dev',dir).identity.userId,'u1')
 writeFileSync(join(dir,'beta.json'),readFileSync(join(dir,'dev.json')))
 assert.throws(()=>loadAuth('beta',dir),/CORRUPT/)
})
test('拒绝损坏、权限不安全、软链、未知身份和越界存储',()=>{
 const dir=root();saveAuth('dev',identity,storage,dir)
 chmodSync(join(dir,'dev.json'),0o644);assert.throws(()=>loadAuth('dev',dir))
 assert.throws(()=>assertIdentity({userId:'u1'},identity))
 assert.throws(()=>saveAuth('dev',identity,{...storage,origins:[{origin:'https://qianxun.hgj.com'}]},root()))
 assert.throws(()=>saveAuth('dev',identity,{...storage,cookies:[{domain:'.evil.test'}]},root()))
 const target=root();symlinkSync(join(dir,'dev.json'),join(target,'dev.json'));assert.throws(()=>loadAuth('dev',target))
})
