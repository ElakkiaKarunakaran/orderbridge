package com.orderbridge;

import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.model.dataformat.JsonLibrary;

public class OrderRoute extends RouteBuilder {

    @Override
    public void configure() {

        from("timer:orders?period=10000")
            .to("http://localhost:3000/orders")
            .unmarshal().json(JsonLibrary.Jackson)
            .split(body())
            .process(exchange -> {
                System.out.println("Order Received: " + exchange.getMessage().getBody());
            });
    }
}