import { contactConfig } from './contact-config.js?v=hoi-an-1';

export function normalizeWhatsAppNumber(value) {
  const number = String(value ?? '').trim().replace(/[\s()+.-]/g, '');
  if (!/^[1-9]\d{7,14}$/.test(number)) {
    throw new Error('WhatsApp requires a full international phone number.');
  }
  return number;
}

export function buildWhatsAppUrl(number, request, pageUrl) {
  const url = new URL('https://wa.me/' + normalizeWhatsAppNumber(number));
  const page = new URL(pageUrl);
  page.search = '';
  page.hash = '';
  const message = `Hi ${contactConfig.creator}, I visited the HOI AN website and would like to request ${request}.\n\nReference: ${page.href}\nThank you.`;
  url.searchParams.set('text', message);
  return url.href;
}

export function syncDialogScroll() {
  document.body.style.overflow = document.querySelector('dialog[open]') || document.body.classList.contains('tour-expanded') ? 'hidden' : '';
}

export function getContactWhatsAppUrl(config, request, pageUrl) {
  if (config.placeholder) return null;
  return buildWhatsAppUrl(config.whatsappNumber, request, pageUrl);
}

export function initContact() {
  const dialog = document.querySelector('#contact-dialog');
  const link = document.querySelector('#contact-whatsapp');
  const unavailable = document.querySelector('#contact-unavailable');
  let lastTrigger;

  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-download-request]');
    if (!trigger) return;
    event.preventDefault();
    lastTrigger = trigger;
    const request = trigger.dataset.downloadRequest || 'all HOI AN project files';
    document.querySelector('#contact-request').textContent = request;
    try {
      const href = getContactWhatsAppUrl(contactConfig, request, location.href);
      if (!href) throw new Error('Demo contact is not a live WhatsApp destination.');
      link.href = href;
      link.removeAttribute('aria-disabled');
      link.removeAttribute('tabindex');
      unavailable.hidden = true;
    } catch {
      link.removeAttribute('href');
      link.setAttribute('aria-disabled', 'true');
      link.setAttribute('tabindex', '-1');
      unavailable.hidden = false;
    }
    unavailable.textContent = contactConfig.placeholder
      ? `Demo mode — the example number +${contactConfig.whatsappNumber} is not active. Chat will be available once Muhammad Rizky's number is added.`
      : "The WhatsApp number is not configured yet. Chat will be available once the creator's contact details are added.";
    document.querySelector('#contact-note').textContent = contactConfig.placeholder
      ? 'This is a contact feature preview. No messages are sent and no random phone numbers are contacted.'
      : 'Your request is drafted automatically. You still choose Send in WhatsApp.';
    if (!dialog.open) dialog.showModal();
    syncDialogScroll();
    (link.hasAttribute('href') ? link : document.querySelector('#close-contact')).focus({ preventScroll: true });
  });

  document.querySelector('#close-contact').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    syncDialogScroll();
    if (lastTrigger?.isConnected) lastTrigger.focus({ preventScroll: true });
  });
}
