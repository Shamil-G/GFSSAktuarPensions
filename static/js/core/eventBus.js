export const EventBus = {
    debug: false,

    on(eventName, handler, zone = document) {
        zone.addEventListener(eventName, handler);
        if (this.debug) console.log(`🔗 EventBus.on('${eventName}')`);
    },

    off(eventName, handler, zone = document) {
        zone.removeEventListener(eventName, handler);
        if (this.debug) console.log(`❌ EventBus.off('${eventName}')`);
    },

    once(eventName, handler, zone = document) {
        const wrapper = (event) => {
            handler(event);
            zone.removeEventListener(eventName, wrapper);
            if (this.debug) console.log(`☑️ EventBus.once('${eventName}')`);
        };
        zone.addEventListener(eventName, wrapper);
    },

    emit(eventName, detail = {}, zone = document) {
        const event = new CustomEvent(eventName, {
            bubbles: true,
            detail
        });
        zone.dispatchEvent(event);
        if (this.debug) console.log(`📡 EventBus.emit('${eventName}')`, detail);
    },

    scope(zone) {
        return {
            on: (e, h) => this.on(e, h, zone),
            off: (e, h) => this.off(e, h, zone),
            once: (e, h) => this.once(e, h, zone),
            emit: (e, d) => this.emit(e, d, zone)
        };
    },

    forward(fromZone, toZone, eventName) {
        this.on(eventName, (event) => {
            this.emit(eventName, event.detail, toZone);
            if (this.debug) console.log(`🔁 EventBus.forward('${eventName}')`);
        }, fromZone);
    }
};
