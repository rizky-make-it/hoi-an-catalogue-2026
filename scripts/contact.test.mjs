import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeWhatsAppNumber, buildWhatsAppUrl, getContactWhatsAppUrl } from '../dist/contact.js';
import { contactConfig } from '../dist/contact-config.js';

test('published contact uses the creator-provided WhatsApp number, not the demo', () => {
  assert.equal(contactConfig.creator, 'Muhammad Rizky');
  assert.equal(contactConfig.placeholder, false);
  assert.equal(contactConfig.whatsappNumber, '6281393177004');
  const url = new URL(getContactWhatsAppUrl(contactConfig, 'the HOI AN project files', 'https://example.com/'));
  assert.equal(url.pathname, '/6281393177004');
});

test('accepts international format and removes display punctuation', () => {
  assert.equal(normalizeWhatsAppNumber('+1 (555) 123-4567'), '15551234567');
  assert.equal(normalizeWhatsAppNumber('62 812.3456.7890'), '6281234567890');
});

test('rejects missing, local-only, malformed, and excessively long numbers', () => {
  for (const number of ['', null, undefined, '081234567890', '62812invalid3456', '123', '1234567890123456', 'https://example.com']) {
    assert.throws(() => normalizeWhatsAppNumber(number));
  }
});

test('prepares a WhatsApp draft with the selected file and creator credit', () => {
  const request = 'the King Bed GLB model (LV453.B02) & 4K render';
  const url = new URL(buildWhatsAppUrl('15551234567', request, 'https://example.com/hoi-an/?private=value#downloads'));
  assert.equal(url.origin, 'https://wa.me');
  assert.equal(url.pathname, '/15551234567');
  const message = url.searchParams.get('text');
  assert.ok(message.includes('Muhammad Rizky'));
  assert.ok(message.startsWith('Hi Muhammad Rizky, I visited the HOI AN website and would like to request '));
  assert.ok(message.includes('\n\nReference: '));
  assert.ok(message.endsWith('\nThank you.'));
  assert.ok(message.includes(request));
  assert.ok(message.includes('https://example.com/hoi-an/'));
  assert.ok(!message.includes('private=value'));
  assert.ok(!message.includes('#downloads'));
});

test('encodes file names as text, not extra URL parameters', () => {
  const request = 'render "Dining" & text=another message + #4K';
  const url = new URL(buildWhatsAppUrl('15551234567', request, 'https://example.com/hoi-an/'));
  assert.deepEqual([...url.searchParams.keys()], ['text']);
  assert.ok(url.searchParams.get('text').includes(request));
});

test('placeholder mode never links a visitor to an example phone number', () => {
  assert.equal(getContactWhatsAppUrl({placeholder:true,whatsappNumber:'6200000000000'}, 'all files', 'https://example.com/'), null);
});

test('live contact mode prepares a link only after the placeholder is removed', () => {
  const url = new URL(getContactWhatsAppUrl({placeholder:false,whatsappNumber:'15551234567'}, 'the Blender file', 'https://example.com/'));
  assert.equal(url.pathname, '/15551234567');
  assert.ok(url.searchParams.get('text').includes('the Blender file'));
});
