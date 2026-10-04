package com.saas.audit.infrastructure.messaging;

import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.amqp.support.converter.JacksonJsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import tools.jackson.databind.json.JsonMapper;

@Configuration
public class AuditMessagingConfig {

    /**
     * Fila durável: as mensagens sobrevivem a um restart do broker. O que for
     * rejeitado sem volta é desviado para a fila {@code <fila>.dlq}, onde fica
     * visível para conferência em vez de sumir. A declaração precisa ser idêntica
     * à da aplicação principal, que também declara a fila.
     */
    @Bean
    Queue auditEventsQueue(@Value("${audit.messaging.queue}") String queue) {
        return QueueBuilder.durable(queue)
                .deadLetterExchange("")
                .deadLetterRoutingKey(queue + ".dlq")
                .build();
    }

    @Bean
    Queue auditEventsDeadLetterQueue(@Value("${audit.messaging.queue}") String queue) {
        return QueueBuilder.durable(queue + ".dlq").build();
    }

    /**
     * O tipo de destino vem do parâmetro do listener, não do cabeçalho {@code __TypeId__}
     * que o produtor grava: o nome da classe do produtor não existe neste serviço.
     */
    @Bean
    MessageConverter auditMessageConverter(JsonMapper jsonMapper) {
        JacksonJsonMessageConverter converter = new JacksonJsonMessageConverter(jsonMapper);
        converter.setAlwaysConvertToInferredType(true);
        return converter;
    }

}
