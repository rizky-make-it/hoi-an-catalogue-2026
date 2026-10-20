export function joystickVector(dx, dy, radius = 36) {
  const distance = Math.hypot(dx, dy);
  if (!Number.isFinite(distance) || radius <= 0 || !Number.isFinite(radius)) return {x: 0, y: 0};
  const strength = Math.min(1, distance / radius);
  const speed = Math.max(0, (strength - .14) / .86);
  return distance ? {x: dx / distance * speed, y: -dy / distance * speed} : {x: 0, y: 0};
}

export function createJoystick(element, onChange) {
  const thumb = element.querySelector('.joystick-thumb');
  let pointerId = null;
  const reset = () => {
    const previous = pointerId;
    pointerId = null;
    thumb.style.transform = 'translate(0px, 0px)';
    element.classList.remove('is-active');
    onChange({x: 0, y: 0});
    if (previous !== null && element.hasPointerCapture(previous)) element.releasePointerCapture(previous);
  };
  const update = event => {
    const rect = element.getBoundingClientRect(), radius = rect.width * .3;
    const dx = event.clientX - rect.left - rect.width / 2, dy = event.clientY - rect.top - rect.height / 2;
    const distance = Math.hypot(dx, dy), scale = distance > radius ? radius / distance : 1;
    thumb.style.transform = `translate(${dx * scale}px, ${dy * scale}px)`;
    onChange(joystickVector(dx, dy, radius));
  };
  element.addEventListener('pointerdown', event => {
    if (pointerId !== null || (event.pointerType === 'mouse' && event.button !== 0)) return;
    event.preventDefault();
    pointerId = event.pointerId;
    element.setPointerCapture(pointerId);
    element.classList.add('is-active');
    update(event);
  });
  element.addEventListener('pointermove', event => {if (event.pointerId === pointerId) update(event);});
  for (const name of ['pointerup', 'pointercancel', 'lostpointercapture']) {
    element.addEventListener(name, event => {if (event.pointerId === pointerId) reset();});
  }
  return {reset};
}
