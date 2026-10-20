import test from 'node:test';
import assert from 'node:assert/strict';
import {joystickVector} from '../dist/touch-controls.js';

test('joystick rests at zero and ignores tiny thumb movements', () => {
  assert.deepEqual(joystickVector(0, 0), {x:0, y:0});
  assert.equal(Math.hypot(...Object.values(joystickVector(2, 2))), 0);
});
test('joystick maps screen up to forward and right to strafe', () => {
  assert.equal(joystickVector(0, -36).y, 1);
  assert.equal(joystickVector(36, 0).x, 1);
  assert.equal(joystickVector(0, 36).y, -1);
  assert.equal(joystickVector(-36, 0).x, -1);
});
test('diagonal and out-of-bounds gestures never exceed walking speed', () => {
  for (const [x,y] of [[36,36],[500,-100],[0,200],[-200,400]]) {
    const value=joystickVector(x,y);
    assert.ok(Math.abs(Math.hypot(value.x,value.y)-1)<1e-12);
  }
});
test('short drags produce slower analogue movement', () => {
  const half=joystickVector(18,0);
  assert.ok(half.x>0&&half.x<.5);
});
test('invalid input cannot corrupt the camera position', () => {
  for(const args of [[NaN,0],[Infinity,0],[0,0,0],[1,1,-1],[1,1,Infinity]]) {
    assert.deepEqual(joystickVector(...args),{x:0,y:0});
  }
});
